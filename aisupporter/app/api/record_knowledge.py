from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import pandas as pd
import duckdb
import os
import io
import json
import random
from datetime import datetime, timedelta
import numpy as np
import traceback

# 프로젝트 유틸리티 가져오기
from app.utils.parquet_generator import generate_parquet_data

# 라우터 정의
router = APIRouter()

# 데이터 디렉토리 경로 설정
PARQUET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'parquet')

# 응답 모델 정의
class RecordKnowledgeResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    summary: Dict[str, Any] = None
    error: Optional[str] = None

class DataDetailsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]] = None
    pagination: Dict[str, Any] = None
    error: Optional[str] = None

class GenerateDataResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    files_created: Optional[List[str]] = None

# 주요 API 엔드포인트: 기록지식 데이터 조회
@router.get("/record-knowledge", response_model=RecordKnowledgeResponse)
async def get_record_knowledge(
    region: str = Query("all", description="필터링할 지역"),
    type: str = Query("all", description="필터링할 데이터 유형"),
    period: str = Query("2year", description="조회 기간(6month, 1year, 2year)")
):
    try:
        # 기간에 따른 시작일 계산
        end_date = datetime.now()
        if period == "6month":
            start_date = end_date - timedelta(days=180)
        elif period == "1year":
            start_date = end_date - timedelta(days=365)
        else:  # 기본값: 2year
            start_date = end_date - timedelta(days=730)
        
        # DuckDB 연결
        conn = duckdb.connect(database=':memory:')
        
        # 요약 데이터 가져오기
        summary = get_data_summary(conn)
        
        # 차트용 데이터 가져오기
        chart_data = get_chart_data(conn, region, type, start_date, end_date)
        
        return {
            "success": True,
            "data": chart_data,
            "summary": summary
        }
    
    except Exception as e:
        print(f"기록지식 데이터 조회 오류: {str(e)}")
        print(traceback.format_exc())
        
        # 오류 시 샘플 데이터 반환 (개발/테스트용)
        return {
            "success": True,
            "data": generate_sample_chart_data(),
            "summary": generate_sample_summary(),
            "error": f"실제 데이터 조회 실패 (샘플 데이터 반환): {str(e)}"
        }

# 상세 데이터 조회 API
@router.get("/record-knowledge/details", response_model=DataDetailsResponse)
async def get_record_details(
    region: str = Query("all", description="필터링할 지역"),
    type: str = Query("all", description="필터링할 데이터 유형"),
    page: int = Query(1, description="페이지 번호"),
    per_page: int = Query(5, description="페이지당 항목 수")
):
    try:
        # DuckDB 연결
        conn = duckdb.connect(database=':memory:')
        
        # 데이터 유형별 파일 경로
        file_paths = {}
        if type == "all" or type == "environment":
            env_path = os.path.join(PARQUET_DIR, 'environment_data.parquet')
            if os.path.exists(env_path):
                file_paths["environment"] = env_path
        
        if type == "all" or type == "pest":
            pest_path = os.path.join(PARQUET_DIR, 'pest_data.parquet')
            if os.path.exists(pest_path):
                file_paths["pest"] = pest_path
        
        if type == "all" or type == "growth":
            growth_path = os.path.join(PARQUET_DIR, 'growth_data.parquet')
            if os.path.exists(growth_path):
                file_paths["growth"] = growth_path
        
        if type == "all" or type == "moisture":
            moisture_path = os.path.join(PARQUET_DIR, 'moisture_data.parquet')
            if os.path.exists(moisture_path):
                file_paths["moisture"] = moisture_path
        
        if type == "all" or type == "nutrition":
            nutrition_path = os.path.join(PARQUET_DIR, 'nutrition_data.parquet')
            if os.path.exists(nutrition_path):
                file_paths["nutrition"] = nutrition_path
        
        if type == "all" or type == "control":
            control_path = os.path.join(PARQUET_DIR, 'control_data.parquet')
            if os.path.exists(control_path):
                file_paths["control"] = control_path
        
        # 파일이 없는 경우
        if not file_paths:
            return {
                "success": True,
                "data": generate_sample_details(),
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": 100,
                    "total_pages": 20
                }
            }
        
        # 쿼리 구성
        results = []
        total_items = 0
        
        for data_type, file_path in file_paths.items():
            # 지역 필터링
            region_filter = ""
            if region != "all":
                region_filter = f"WHERE region = '{region}'"
            
            # 총 항목 수 계산 쿼리
            count_query = f"""
                SELECT COUNT(*) as count
                FROM parquet_scan('{file_path}')
                {region_filter}
            """
            count_result = conn.execute(count_query).fetchone()
            
            if count_result:
                total_items += count_result[0]
            
            # 데이터 조회 쿼리
            offset = (page - 1) * per_page
            limit = per_page
            
            data_query = f"""
                SELECT *
                FROM parquet_scan('{file_path}')
                {region_filter}
                ORDER BY timestamp DESC
                LIMIT {limit} OFFSET {offset}
            """
            
            data_result = conn.execute(data_query).fetchall()
            column_names = [desc[0] for desc in conn.description]
            
            # 결과 형식 변환
            for row in data_result:
                item = {column_names[i]: value for i, value in enumerate(row)}
                item['type'] = data_type
                item['type_kr'] = get_type_kr_name(data_type)
                results.append(item)
        
        # 결과 정렬 (최신순)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 페이지 크기로 잘라내기
        paginated_results = results[:per_page]
        
        # 페이지네이션 정보
        total_pages = (total_items + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": paginated_results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }
    
    except Exception as e:
        print(f"상세 데이터 조회 오류: {str(e)}")
        print(traceback.format_exc())
        
        # 오류 시 샘플 데이터 반환 (개발/테스트용)
        return {
            "success": True,
            "data": generate_sample_details(),
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": 100,
                "total_pages": 20
            },
            "error": f"실제 데이터 조회 실패 (샘플 데이터 반환): {str(e)}"
        }

# 데이터 다운로드 API
@router.get("/record-knowledge/download")
async def download_record_data(
    format: str = Query("csv", description="다운로드 형식 (csv 또는 excel)"),
    region: str = Query("all", description="필터링할 지역"),
    type: str = Query("all", description="필터링할 데이터 유형"),
    period: str = Query("2year", description="조회 기간")
):
    try:
        # 기간에 따른 시작일 계산
        end_date = datetime.now()
        if period == "6month":
            start_date = end_date - timedelta(days=180)
        elif period == "1year":
            start_date = end_date - timedelta(days=365)
        else:  # 기본값: 2year
            start_date = end_date - timedelta(days=730)
        
        # DuckDB 연결
        conn = duckdb.connect(database=':memory:')
        
        # 데이터 유형별 파일 경로
        file_paths = {}
        if type == "all" or type == "environment":
            env_path = os.path.join(PARQUET_DIR, 'environment_data.parquet')
            if os.path.exists(env_path):
                file_paths["environment"] = env_path
        
        # 다른 데이터 유형도 추가
        if type == "all" or type == "pest":
            pest_path = os.path.join(PARQUET_DIR, 'pest_data.parquet')
            if os.path.exists(pest_path):
                file_paths["pest"] = pest_path
                
        # 나머지 데이터 유형도 추가...
        if type == "all" or type == "growth":
            growth_path = os.path.join(PARQUET_DIR, 'growth_data.parquet')
            if os.path.exists(growth_path):
                file_paths["growth"] = growth_path
                
        if type == "all" or type == "moisture":
            moisture_path = os.path.join(PARQUET_DIR, 'moisture_data.parquet')
            if os.path.exists(moisture_path):
                file_paths["moisture"] = moisture_path
                
        if type == "all" or type == "nutrition":
            nutrition_path = os.path.join(PARQUET_DIR, 'nutrition_data.parquet')
            if os.path.exists(nutrition_path):
                file_paths["nutrition"] = nutrition_path
                
        if type == "all" or type == "control":
            control_path = os.path.join(PARQUET_DIR, 'control_data.parquet')
            if os.path.exists(control_path):
                file_paths["control"] = control_path
        
        # 파일이 없는 경우
        if not file_paths:
            # 예시 데이터 생성
            output = io.BytesIO()
            
            sample_df = pd.DataFrame({
                'id': [f'SAMPLE{i}' for i in range(1, 11)],
                'data_type': ['sample'] * 10,
                'region': ['샘플 지역'] * 10,
                'timestamp': [datetime.now() - timedelta(days=i) for i in range(10)],
                'value': [f'샘플 데이터 {i}' for i in range(1, 11)]
            })
            
            if format == 'excel':
                sample_df.to_excel(output, index=False)
                media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                extension = 'xlsx'
            else:  # CSV
                sample_df.to_csv(output, index=False)
                media_type = 'text/csv'
                extension = 'csv'
            
            output.seek(0)
            filename = f'sample_data.{extension}'
            
            return StreamingResponse(
                output,
                media_type=media_type,
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        
        # 데이터프레임 리스트 준비
        dataframes = []
        
        for data_type, file_path in file_paths.items():
            # 지역 및 기간 필터링
            filters = []
            if region != "all":
                filters.append(f"region = '{region}'")
            
            # 시간 필터는 항상 적용
            filters.append(f"timestamp >= '{start_date}' AND timestamp <= '{end_date}'")
            
            where_clause = ""
            if filters:
                where_clause = "WHERE " + " AND ".join(filters)
            
            # 데이터 조회
            query = f"""
                SELECT *
                FROM parquet_scan('{file_path}')
                {where_clause}
                ORDER BY timestamp DESC
            """
            
            try:
                df = conn.execute(query).fetch_df()
                if not df.empty:
                    # 데이터 유형 열 추가
                    df['data_type'] = data_type
                    dataframes.append(df)
            except Exception as e:
                print(f"데이터 조회 오류({data_type}): {str(e)}")
        
        # 데이터가 없는 경우
        if not dataframes:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "선택한 필터에 해당하는 데이터가 없습니다."}
            )
        
        # 데이터프레임 합치기
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        # 출력 파일 형식 지정
        output = io.BytesIO()
        
        if format == 'excel':
            combined_df.to_excel(output, index=False)
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        else:  # CSV
            combined_df.to_csv(output, index=False)
            media_type = 'text/csv'
            extension = 'csv'
        
        output.seek(0)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_type_part = type if type != "all" else "all"
        region_part = region if region != "all" else "all"
        filename = f'agri_data_{data_type_part}_{region_part}_{timestamp}.{extension}'
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    
    except Exception as e:
        print(f"데이터 다운로드 오류: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"데이터 다운로드 중 오류 발생: {str(e)}"}
        )

# 테스트 데이터 생성 API
@router.post("/generate-parquet", response_model=GenerateDataResponse)
async def generate_parquet_data_api(days: int = Query(730, description="생성할 데이터의 일수")):
    try:
        # 데이터 디렉토리 확인 및 생성
        os.makedirs(PARQUET_DIR, exist_ok=True)
        
        # 데이터 생성 함수 호출
        result = generate_parquet_data(days)
        
        return result
    except Exception as e:
        print(f"데이터 생성 오류: {str(e)}")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": f"데이터 생성 중 오류 발생: {str(e)}"
        }

# 유틸리티 함수들
def get_data_summary(conn):
    """DuckDB에서 데이터 요약 정보 가져오기"""
    summary_path = os.path.join(PARQUET_DIR, 'agri_data_summary.parquet')
    
    if os.path.exists(summary_path):
        try:
            query = f"SELECT * FROM parquet_scan('{summary_path}') LIMIT 1"
            result = conn.execute(query).fetchone()
            
            if result:
                column_names = [desc[0] for desc in conn.description]
                summary = {column_names[i]: value for i, value in enumerate(result)}
                return summary
        except Exception as e:
            print(f"요약 데이터 조회 오류: {str(e)}")
    
    # 기본 요약 데이터 생성
    return generate_sample_summary()

def get_chart_data(conn, region, data_type, start_date, end_date):
    """DuckDB에서 차트 데이터 가져오기"""
    try:
        # 월별 데이터 수집을 위한 컨테이너
        monthly_data = {}
        
        # 데이터 파일 확인
        has_parquet_files = False
        for file_name in ['environment_data.parquet', 'pest_data.parquet', 'growth_data.parquet', 
                         'moisture_data.parquet', 'nutrition_data.parquet', 'control_data.parquet']:
            if os.path.exists(os.path.join(PARQUET_DIR, file_name)):
                has_parquet_files = True
                break
        
        if not has_parquet_files:
            return generate_sample_chart_data()
        
        # 환경 데이터 (온도, 습도)는 모든 시기에 표시
        if data_type == "all" or data_type == "environment":
            env_file = os.path.join(PARQUET_DIR, 'environment_data.parquet')
            if os.path.exists(env_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           AVG(temperature) as avg_temp,
                           AVG(humidity) as avg_humidity
                    FROM parquet_scan('{env_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, avg_temp, avg_humidity = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['temperature'] = round(avg_temp, 1) if avg_temp is not None else None
                    monthly_data[month]['humidity'] = round(avg_humidity, 1) if avg_humidity is not None else None
        
        # 다른 데이터들은 6월~10월 기간만 표시
        months = sorted(list(monthly_data.keys()))
        for month in months:
            # 월 추출 (YYYY-MM 형식에서 MM 부분)
            month_num = int(month.split('-')[1])
            is_active_season = month_num >= 6 and month_num <= 10
            
            if not is_active_season:
                # 활동 시즌이 아닌 경우 농업 데이터는 null 또는 0으로 설정
                monthly_data[month]['ndvi'] = None
                monthly_data[month]['soil_moisture'] = None
                monthly_data[month]['nutrition'] = None
                monthly_data[month]['pest_occurrence'] = 0
                monthly_data[month]['treatment_frequency'] = 0
                continue  # 다른 데이터 처리 건너뛰기
        
        # 성장기(6월~10월)에만 농업 데이터 가져오기
        if data_type == "all" or data_type == "growth":
            growth_file = os.path.join(PARQUET_DIR, 'growth_data.parquet')
            if os.path.exists(growth_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                # 6월~10월 데이터만 필터링
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           AVG(ndvi) as avg_ndvi
                    FROM parquet_scan('{growth_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    AND (
                        (EXTRACT(MONTH FROM timestamp) >= 6 AND EXTRACT(MONTH FROM timestamp) <= 10)
                    )
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, avg_ndvi = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['ndvi'] = round(avg_ndvi, 2) if avg_ndvi is not None else None
        
        # 수분 데이터 (토양 수분) - 6월~10월만
        if data_type == "all" or data_type == "moisture":
            moisture_file = os.path.join(PARQUET_DIR, 'moisture_data.parquet')
            if os.path.exists(moisture_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           AVG(soil_moisture) as avg_soil_moisture
                    FROM parquet_scan('{moisture_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    AND (
                        (EXTRACT(MONTH FROM timestamp) >= 6 AND EXTRACT(MONTH FROM timestamp) <= 10)
                    )
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, avg_soil_moisture = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['soil_moisture'] = round(avg_soil_moisture, 1) if avg_soil_moisture is not None else None
        
        # 영양 데이터 (NPK 평균) - 6월~10월만
        if data_type == "all" or data_type == "nutrition":
            nutrition_file = os.path.join(PARQUET_DIR, 'nutrition_data.parquet')
            if os.path.exists(nutrition_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           AVG(n_value + p_value + k_value) / 3 as avg_nutrition
                    FROM parquet_scan('{nutrition_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    AND (
                        (EXTRACT(MONTH FROM timestamp) >= 6 AND EXTRACT(MONTH FROM timestamp) <= 10)
                    )
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, avg_nutrition = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['nutrition'] = round(avg_nutrition, 1) if avg_nutrition is not None else None
        
        # 병해충 데이터 (발생 건수) - 6월~10월만
        if data_type == "all" or data_type == "pest":
            pest_file = os.path.join(PARQUET_DIR, 'pest_data.parquet')
            if os.path.exists(pest_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           COUNT(*) as pest_count
                    FROM parquet_scan('{pest_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    AND (
                        (EXTRACT(MONTH FROM timestamp) >= 6 AND EXTRACT(MONTH FROM timestamp) <= 10)
                    )
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, pest_count = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['pest_occurrence'] = pest_count
        
        # 제어 이력 데이터 (처리 횟수) - 6월~10월만
        if data_type == "all" or data_type == "control":
            control_file = os.path.join(PARQUET_DIR, 'control_data.parquet')
            if os.path.exists(control_file):
                region_filter = "" if region == "all" else f"AND region = '{region}'"
                
                query = f"""
                    SELECT strftime(timestamp, '%Y-%m') as month,
                           COUNT(*) as treatment_count
                    FROM parquet_scan('{control_file}')
                    WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}'
                    AND (
                        (EXTRACT(MONTH FROM timestamp) >= 6 AND EXTRACT(MONTH FROM timestamp) <= 10)
                    )
                    {region_filter}
                    GROUP BY month
                    ORDER BY month
                """
                
                result = conn.execute(query).fetchall()
                
                for row in result:
                    month, treatment_count = row
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    
                    monthly_data[month]['treatment_frequency'] = treatment_count
        
        # 데이터가 없는 경우
        if not monthly_data:
            return generate_sample_chart_data()
        
        # 누락된 필드에 기본값 0 또는 null 설정
        months = sorted(monthly_data.keys())
        for month in months:
            month_num = int(month.split('-')[1])
            is_active_season = month_num >= 6 and month_num <= 10
            
            monthly_data[month].setdefault('temperature', None)
            monthly_data[month].setdefault('humidity', None)
            
            # 성장기(6월~10월)에만 농업 데이터 표시
            if is_active_season:
                monthly_data[month].setdefault('ndvi', None)
                monthly_data[month].setdefault('soil_moisture', None)
                monthly_data[month].setdefault('nutrition', None)
                monthly_data[month].setdefault('pest_occurrence', 0)
                monthly_data[month].setdefault('treatment_frequency', 0)
            else:
                monthly_data[month]['ndvi'] = None
                monthly_data[month]['soil_moisture'] = None
                monthly_data[month]['nutrition'] = None
                monthly_data[month]['pest_occurrence'] = 0
                monthly_data[month]['treatment_frequency'] = 0
        
        # 차트 데이터 형식으로 변환
        chart_data = {
            'timestamps': months,
            'temperature': [monthly_data[month]['temperature'] for month in months],
            'humidity': [monthly_data[month]['humidity'] for month in months],
            'ndvi': [monthly_data[month]['ndvi'] for month in months],
            'soil_moisture': [monthly_data[month]['soil_moisture'] for month in months],
            'nutrition': [monthly_data[month]['nutrition'] for month in months],
            'pest_occurrence': [monthly_data[month]['pest_occurrence'] for month in months],
            'treatment_frequency': [monthly_data[month]['treatment_frequency'] for month in months]
        }
        
        return chart_data
    
    except Exception as e:
        print(f"차트 데이터 조회 오류: {str(e)}")
        print(traceback.format_exc())
        return generate_sample_chart_data()

def get_type_kr_name(data_type):
    """데이터 유형에 대한 한글 이름 반환"""
    type_names = {
        'environment': '환경',
        'pest': '병해충',
        'growth': '생육',
        'moisture': '수분',
        'nutrition': '영양',
        'control': '제어'
    }
    return type_names.get(data_type, '기타')

def generate_sample_summary():
    """샘플 요약 데이터 생성"""
    return {
        'environment_count': 12485,
        'growth_count': 589,
        'moisture_count': 2456,
        'nutrition_count': 1782,
        'pest_count': 1843,
        'control_count': 3651,
        'irrigation_count': 3842,
        'pesticide_count': 1254,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_sample_chart_data():
    """샘플 차트 데이터 생성"""
    # 최근 24개월 데이터 생성
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    # 월별 타임스탬프 생성
    current = start_date
    months = []
    while current <= end_date:
        months.append(current.strftime('%Y-%m'))
        # 다음 달로 이동
        year = current.year + (current.month // 12)
        month = (current.month % 12) + 1
        current = datetime(year, month, 1)
    
    # 데이터 시리즈 생성
    temps = []
    humidity = []
    ndvi = []
    soil_moisture = []
    nutrition = []
    pest_occurrence = []
    treatment_frequency = []
    
    for i, month in enumerate(months):
        # 계절성을 시뮬레이션하기 위한 월 숫자 (1-12)
        month_num = int(month.split('-')[1])
        
        # 한국의 계절 특성에 맞게 온도 설정
        if month_num in [12, 1, 2]:  # 겨울
            # 겨울철 평균 기온: -5 ~ 5도
            base_temp = -2
            temp_variation = 4
            season_name = "겨울"
        elif month_num in [3, 4, 5]:  # 봄
            # 봄 평균 기온: 5 ~ 20도로 점진적 상승
            progress = (month_num - 3) / 3
            base_temp = 5 + progress * 15
            temp_variation = 3
            season_name = "봄"
        elif month_num in [6, 7, 8]:  # 여름
            # 7-8월이 가장 더움 (25-32도), 6월은 약간 낮음
            if month_num == 7 or month_num == 8:
                base_temp = 30
            else:
                base_temp = 25
            temp_variation = 2
            season_name = "여름"
        else:  # 가을 (9, 10, 11)
            # 가을 평균 기온: 점진적 하강 20 ~ 5도
            progress = (11 - month_num) / 3
            base_temp = 5 + progress * 15
            temp_variation = 3
            season_name = "가을"
        
        # 온도에 약간의 랜덤 변동 추가
        temps.append(round(base_temp + np.random.normal(0, temp_variation), 1))
        
        # 습도: 계절 특성 반영
        if season_name == "여름":
            # 여름에는 습도가 높음 (장마 및 폭염 기간)
            base_humidity = 75
        elif season_name == "겨울":
            # 겨울에는 습도가 낮음 (건조함)
            base_humidity = 40
        else:
            # 봄, 가을은 중간 정도
            base_humidity = 60
            
        humidity.append(round(base_humidity + np.random.normal(0, 5), 1))
        
        # 6월~10월 (여름과 초가을)에만 농업활동 데이터 생성
        is_active_season = month_num >= 6 and month_num <= 10
        
        # NDVI: 성장기간(6월~10월)에만 데이터 생성, 그 외에는 null
        if is_active_season:
            # 7-8월에 NDVI 최대
            if month_num in [7, 8]:
                ndvi_base = 0.7
            elif month_num == 9:
                ndvi_base = 0.6
            elif month_num == 10:
                ndvi_base = 0.4
            else:  # 6월
                ndvi_base = 0.5
                
            ndvi.append(round(ndvi_base + np.random.normal(0, 0.05), 2))
        else:
            ndvi.append(None)
        
        # 토양 수분: 성장기간에만 데이터 생성
        if is_active_season:
            # 장마철 7월에 토양 수분 최대
            if month_num == 7:
                moisture_base = 55
            else:
                moisture_base = 45
                
            soil_moisture.append(round(moisture_base + np.random.normal(0, 5), 1))
        else:
            soil_moisture.append(None)
        
        # 영양 상태: 성장기간에만 데이터 생성
        if is_active_season:
            nutrition.append(round(65 + np.random.normal(0, 5), 1))
        else:
            nutrition.append(None)
        
        # 병해충 발생: 성장기간에만 발생, 특히 여름(7-8월)에 높음
        if is_active_season:
            # 고온다습한 7-8월에 병해충 발생 최대
            if month_num in [7, 8]:
                pest_base = 7
            else:
                pest_base = 3
                
            pest_occurrence.append(round(pest_base + np.random.normal(0, 1)))
        else:
            pest_occurrence.append(0)
        
        # 관수/관비/농약살포 등 처리 횟수: 성장기간에만 처리
        if is_active_season:
            # 성장기 및 병해충 많은 시기에 처리 횟수 증가
            if month_num in [7, 8]:
                treatment_base = 5
            else:
                treatment_base = 2
                
            treatment_frequency.append(round(treatment_base + np.random.normal(0, 1)))
        else:
            treatment_frequency.append(0)
    
    return {
        'timestamps': months,
        'temperature': temps,
        'humidity': humidity,
        'ndvi': ndvi,
        'soil_moisture': soil_moisture,
        'nutrition': nutrition,
        'pest_occurrence': pest_occurrence,
        'treatment_frequency': treatment_frequency
    }

def generate_sample_details():
    """샘플 상세 데이터 생성"""
    data_types = ['environment', 'pest', 'growth', 'moisture', 'nutrition', 'control']
    regions = ['김제지구', '태안지구', '밀양지구']
    
    sample_data = []
    
    for i in range(5):  # 5개 항목 생성
        data_type = random.choice(data_types)
        
        item = {
            'id': f"{data_type[:3].upper()}{random.randint(1000, 9999)}",
            'type': data_type,
            'type_kr': get_type_kr_name(data_type),
            'region': random.choice(regions),
            'timestamp': (datetime.now() - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 데이터 유형별 값 생성
        if data_type == 'environment':
            temp = round(random.uniform(10, 35), 1)
            humidity = round(random.uniform(40, 90), 1)
            item['value'] = f"온도: {temp}°C, 습도: {humidity}%"
        elif data_type == 'pest':
            pests = ["진딧물", "응애", "나방류", "흰가루병", "역병"]
            item['value'] = f"{random.choice(pests)} 발생, 심각도: {random.randint(1, 5)}/5"
        elif data_type == 'growth':
            ndvi = round(random.uniform(0.3, 0.9), 2)
            leaf = round(random.uniform(5, 15), 1)
            item['value'] = f"NDVI: {ndvi}, 잎 크기: {leaf}cm"
        elif data_type == 'moisture':
            moisture = round(random.uniform(20, 80), 1)
            item['value'] = f"토양 수분: {moisture}%, 토양 온도: {round(random.uniform(10, 30), 1)}°C"
        elif data_type == 'nutrition':
            n = round(random.uniform(30, 90), 1)
            p = round(random.uniform(30, 90), 1)
            k = round(random.uniform(30, 90), 1)
            item['value'] = f"질소(N): {n}, 인(P): {p}, 칼륨(K): {k}"
        elif data_type == 'control':
            controls = ["자동 관수", "질소 비료 시비", "살충제 살포", "살균제 살포"]
            item['value'] = f"{random.choice(controls)}, {random.randint(20, 60)}분 작동"
        
        sample_data.append(item)
    
    return sample_data 