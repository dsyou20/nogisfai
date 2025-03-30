import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import pyarrow as pa
import pyarrow.parquet as pq
import logging
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 경로 설정
PARQUET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'parquet')

# 지역 데이터
REGIONS = ['김제지구', '태안지구', '밀양지구']

# 데이터 생성 함수
def generate_parquet_data(days=730):
    """
    농업 데이터를 생성하여 Parquet 형식으로 저장합니다.
    
    Args:
        days (int): 생성할 데이터의 일수 (기본값: 730일 - 2년)
    
    Returns:
        dict: 생성된 데이터 요약 정보
    """
    try:
        logger.info(f"데이터 생성 시작: {days}일 분량")
        
        # Parquet 디렉토리 생성
        os.makedirs(PARQUET_DIR, exist_ok=True)
        
        # 오늘 날짜
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 날짜 범위 생성
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # 데이터 유형별 파일 생성
        generate_environment_data(date_range)
        generate_moisture_data(date_range)
        generate_nutrition_data(date_range)
        generate_pest_data(date_range)
        generate_growth_data(date_range)
        generate_control_data(date_range)
        
        # 데이터 요약 생성
        generate_summary_data()
        
        logger.info("데이터 생성 완료")
        
        return {
            "success": True,
            "message": f"{days}일 분량의 데이터가 생성되었습니다.",
            "files_created": os.listdir(PARQUET_DIR)
        }
    
    except Exception as e:
        logger.error(f"데이터 생성 오류: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"데이터 생성 중 오류 발생: {str(e)}"
        }

def generate_environment_data(date_range):
    """환경 데이터(온도, 습도 등) 생성"""
    logger.info("환경 데이터 생성 중...")
    
    data = []
    
    for region in REGIONS:
        for date in date_range:
            # 환경 관련 데이터 생성
            environment_data = generate_environment_data(date, region)
            
            data.append({
                'region': region,
                'timestamp': date,
                'temperature': environment_data['temperature'],
                'humidity': environment_data['humidity'],
                'co2': round(random.uniform(350, 500), 1),
                'light_intensity': round(random.uniform(0, 100000) * (0.1 if date.hour < 6 or date.hour > 18 else 1), 1)
            })
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(data)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(PARQUET_DIR, 'environment_data.parquet'))
    
    logger.info(f"환경 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def generate_moisture_data(date_range):
    """토양 수분 데이터 생성"""
    logger.info("수분 데이터 생성 중...")
    
    # 3시간 간격으로 데이터 샘플링
    sampled_dates = date_range[::3]
    
    data = []
    
    for region in REGIONS:
        base_moisture = 60 if region == '태안지구' else (65 if region == '김제지구' else 55)
        
        for date in sampled_dates:
            # 계절성 추가 (여름에 더 건조)
            month = date.month
            season_effect = -5 * np.sin((month - 1) * np.pi / 6)
            
            # 시간에 따른 변동 (밤에 습도 증가)
            hour_effect = 3 * np.sin(date.hour * np.pi / 12)
            
            moisture = base_moisture + season_effect + hour_effect + np.random.normal(0, 2)
            moisture = min(max(moisture, 10), 95)
            
            data.append({
                'region': region,
                'timestamp': date,
                'soil_moisture': round(moisture, 1),
                'soil_temp': round(15 + 10 * np.sin((month - 1) * np.pi / 6) + np.random.normal(0, 1), 1)
            })
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(data)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(PARQUET_DIR, 'moisture_data.parquet'))
    
    logger.info(f"수분 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def generate_nutrition_data(date_range):
    """영양 상태 데이터 생성"""
    logger.info("영양 데이터 생성 중...")
    
    # 12시간 간격으로 데이터 샘플링
    sampled_dates = date_range[::12]
    
    data = []
    
    for region in REGIONS:
        # 지역별 기본 영양 설정
        base_n = 7 if region == '태안지구' else (8 if region == '김제지구' else 6)
        base_p = 6 if region == '태안지구' else (7 if region == '김제지구' else 5)
        base_k = 5 if region == '태안지구' else (6 if region == '김제지구' else 4)
        
        for date in sampled_dates:
            # 계절에 따른 변화
            month = date.month
            season_effect = np.sin((month - 1) * np.pi / 6)
            
            # 시간이 지남에 따라 영양분 소모 (재배 주기 시뮬레이션)
            day_of_year = date.timetuple().tm_yday
            cycle_effect = np.sin(day_of_year * 2 * np.pi / 365)
            
            n_value = base_n + season_effect - cycle_effect + np.random.normal(0, 0.5)
            p_value = base_p + 0.5 * season_effect - cycle_effect + np.random.normal(0, 0.5)
            k_value = base_k + 0.3 * season_effect - cycle_effect + np.random.normal(0, 0.5)
            
            # 범위 제한
            n_value = min(max(n_value, 1), 10)
            p_value = min(max(p_value, 1), 10)
            k_value = min(max(k_value, 1), 10)
            
            data.append({
                'region': region,
                'timestamp': date,
                'n_value': round(n_value, 1),
                'p_value': round(p_value, 1),
                'k_value': round(k_value, 1),
                'ph': round(random.uniform(5.5, 7.0), 1),
                'ec': round(random.uniform(0.5, 3.0), 2)
            })
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(data)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, os.path.join(PARQUET_DIR, 'nutrition_data.parquet'))
    
    logger.info(f"영양 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def generate_pest_data(date_range):
    """병해충 데이터 생성"""
    logger.info("병해충 데이터 생성 중...")
    
    # 병해충 유형
    pest_types = [
        '진딧물', '응애', '나방류', '총채벌레', '굼벵이', 
        '흰가루병', '탄저병', '잿빛곰팡이', '역병', '녹병'
    ]
    
    # 월별 병해충 발생 확률 (0-1, 여름철 확률 증가)
    month_prob = {
        1: 0.05, 2: 0.05, 3: 0.1, 4: 0.2, 5: 0.3, 6: 0.4,
        7: 0.5, 8: 0.5, 9: 0.4, 10: 0.2, 11: 0.1, 12: 0.05
    }
    
    data = []
    
    # 일별로 샘플링
    daily_dates = date_range.normalize().unique()
    
    for region in REGIONS:
        for date in daily_dates:
            # 해당 월의 발생 확률
            base_prob = month_prob[date.month]
            
            # 지역별 변동
            if region == '태안지구':
                region_factor = 0.8  # 서늘한 기후로 병해충 적음
            elif region == '김제지구':
                region_factor = 1.0  # 기준
            else:  # 밀양지구
                region_factor = 1.2  # 따뜻한 기후로 병해충 많음
            
            # 최종 발생 확률
            occurrence_prob = base_prob * region_factor
            
            # 병해충 발생 여부 결정
            if random.random() < occurrence_prob:
                # 발생한 병해충 종류 (1-3개)
                num_pests = random.randint(1, 3)
                selected_pests = random.sample(pest_types, num_pests)
                
                for pest in selected_pests:
                    # 심각도 (1-5)
                    severity = random.randint(1, 5)
                    
                    data.append({
                        'region': region,
                        'timestamp': date,
                        'pest_type': pest,
                        'severity': severity,
                        'location': random.choice(['A구역', 'B구역', 'C구역', 'D구역']),
                        'affected_area': round(random.uniform(0.1, 10.0), 2)  # 영향 면적(m²)
                    })
    
    # DataFrame 생성 및 저장
    if data:  # 데이터가 있는 경우에만 저장
        df = pd.DataFrame(data)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, os.path.join(PARQUET_DIR, 'pest_data.parquet'))
    
    logger.info(f"병해충 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def generate_growth_data(date_range):
    """작물 생육 데이터 생성"""
    logger.info("생육 데이터 생성 중...")
    
    # 주별로 샘플링
    weekly_dates = date_range[::168]  # 7일 * 24시간 = 168
    
    data = []
    
    for region in REGIONS:
        # 작물 종류
        crop = random.choice(['쌀', '배추', '무', '콩', '고추'])
        
        # 재배 시작일 (1년에 2번 작물 재배)
        for year in range(start_date.year, end_date.year + 1):
            for season_start in [datetime(year, 4, 1), datetime(year, 9, 1)]:
                # 생육 기간: 약 100일
                growth_period = 100
                
                # 해당 시즌의 주별 데이터만 필터링
                season_end = season_start + timedelta(days=growth_period)
                season_dates = [d for d in weekly_dates if season_start <= d <= season_end]
                
                if not season_dates:
                    continue
                
                # 정규화된 생육 일수 (0.0 ~ 1.0)
                for i, date in enumerate(season_dates):
                    growth_progress = i / len(season_dates)
                    
                    # 시그모이드 함수로 생장 곡선 모델링
                    def sigmoid(x):
                        return 1 / (1 + np.exp(-10 * (x - 0.5)))
                    
                    # NDVI (식생지수): 생육에 따라 증가 (0.2~0.9)
                    ndvi = 0.2 + 0.7 * sigmoid(growth_progress) + np.random.normal(0, 0.02)
                    ndvi = min(max(ndvi, 0.2), 0.9)
                    
                    # 초장 (cm): 작물별로 다름
                    max_height = {'쌀': 100, '배추': 40, '무': 30, '콩': 60, '고추': 80}[crop]
                    height = max_height * sigmoid(growth_progress) + np.random.normal(0, max_height*0.05)
                    height = max(height, 0)
                    
                    data.append({
                        'region': region,
                        'timestamp': date,
                        'crop': crop,
                        'ndvi': round(ndvi, 2),
                        'height': round(height, 1),
                        'leaf_count': round(5 + 20 * sigmoid(growth_progress) + np.random.normal(0, 2)),
                        'growth_stage': get_growth_stage(growth_progress)
                    })
    
    # DataFrame 생성 및 저장
    if data:
        df = pd.DataFrame(data)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, os.path.join(PARQUET_DIR, 'growth_data.parquet'))
    
    logger.info(f"생육 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def get_growth_stage(progress):
    """생육 단계 결정"""
    if progress < 0.2:
        return '발아기'
    elif progress < 0.4:
        return '영양생장기'
    elif progress < 0.6:
        return '개화기'
    elif progress < 0.8:
        return '결실기'
    else:
        return '성숙기'

def generate_control_data(date_range):
    """관수, 시비, 방제 등 제어 이력 데이터 생성"""
    logger.info("제어 이력 데이터 생성 중...")
    
    # 제어 유형
    control_types = {
        'irrigation': ['점적관수', '살수관수', '저면관수'],
        'fertilization': ['질소 비료', '인산 비료', '칼륨 비료', '복합 비료'],
        'pesticide': ['살충제', '살균제', '제초제', '유기농 방제']
    }
    
    data = []
    
    # 일별 데이터 (하루에 여러 제어 가능)
    daily_dates = date_range.normalize().unique()
    
    for region in REGIONS:
        for date in daily_dates:
            # 관수: 약 3일마다
            if date.day % 3 == 0:
                control_type = 'irrigation'
                method = random.choice(control_types[control_type])
                
                data.append({
                    'region': region,
                    'timestamp': date.replace(hour=random.randint(9, 17)),
                    'control_type': control_type,
                    'method': method,
                    'amount': round(random.uniform(2.0, 5.0), 1),  # L/m²
                    'duration': random.randint(20, 60),  # 분
                    'operator': random.choice(['시스템', '관리자A', '관리자B']),
                    'note': f'{method} 실행'
                })
            
            # 시비: 약 14일마다
            if date.day % 14 == 0:
                control_type = 'fertilization'
                method = random.choice(control_types[control_type])
                
                data.append({
                    'region': region,
                    'timestamp': date.replace(hour=random.randint(9, 17)),
                    'control_type': control_type,
                    'method': method,
                    'amount': round(random.uniform(0.5, 2.0), 1),  # kg/m²
                    'duration': random.randint(30, 90),
                    'operator': random.choice(['시스템', '관리자A', '관리자B']),
                    'note': f'{method} 시비'
                })
            
            # 병해충 방제: 계절적 변동 (여름철에 빈번)
            month_prob = {1: 0.05, 2: 0.05, 3: 0.1, 4: 0.15, 5: 0.2, 6: 0.25,
                          7: 0.3, 8: 0.3, 9: 0.2, 10: 0.15, 11: 0.1, 12: 0.05}
            
            if random.random() < month_prob[date.month]:
                control_type = 'pesticide'
                method = random.choice(control_types[control_type])
                
                data.append({
                    'region': region,
                    'timestamp': date.replace(hour=random.randint(9, 17)),
                    'control_type': control_type,
                    'method': method,
                    'amount': round(random.uniform(0.1, 0.5), 2),  # L/m²
                    'duration': random.randint(30, 120),
                    'operator': random.choice(['시스템', '관리자A', '관리자B']),
                    'note': f'{method} 살포'
                })
    
    # DataFrame 생성 및 저장
    if data:
        df = pd.DataFrame(data)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, os.path.join(PARQUET_DIR, 'control_data.parquet'))
    
    logger.info(f"제어 이력 데이터 생성 완료: {len(data)}개 항목")
    return len(data)

def generate_summary_data():
    """모든 데이터에 대한 요약 통계 생성"""
    logger.info("요약 데이터 생성 중...")
    
    summary = {
        'environment_count': 0,
        'moisture_count': 0,
        'nutrition_count': 0,
        'pest_count': 0,
        'growth_count': 0,
        'control_count': 0,
        'irrigation_count': 0,
        'fertilization_count': 0,
        'pesticide_count': 0,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 각 파일에서 데이터 수 계산
    files = {
        'environment_data.parquet': 'environment_count',
        'moisture_data.parquet': 'moisture_count',
        'nutrition_data.parquet': 'nutrition_count',
        'pest_data.parquet': 'pest_count',
        'growth_data.parquet': 'growth_count',
        'control_data.parquet': 'control_count'
    }
    
    for file, count_key in files.items():
        file_path = os.path.join(PARQUET_DIR, file)
        if os.path.exists(file_path):
            try:
                table = pq.read_table(file_path)
                summary[count_key] = len(table)
            except Exception as e:
                logger.error(f"{file} 읽기 오류: {str(e)}")
    
    # 제어 데이터 세부 분류 계산
    control_file = os.path.join(PARQUET_DIR, 'control_data.parquet')
    if os.path.exists(control_file):
        try:
            control_df = pq.read_table(control_file).to_pandas()
            summary['irrigation_count'] = len(control_df[control_df['control_type'] == 'irrigation'])
            summary['fertilization_count'] = len(control_df[control_df['control_type'] == 'fertilization'])
            summary['pesticide_count'] = len(control_df[control_df['control_type'] == 'pesticide'])
        except Exception as e:
            logger.error(f"제어 데이터 세부 분류 오류: {str(e)}")
    
    # 요약 데이터를 Parquet 파일로 저장
    summary_df = pd.DataFrame([summary])
    summary_table = pa.Table.from_pandas(summary_df)
    pq.write_table(summary_table, os.path.join(PARQUET_DIR, 'agri_data_summary.parquet'))
    
    logger.info("요약 데이터 생성 완료")
    return summary

# 시작 및 종료일 전역 설정
start_date = None
end_date = None

if __name__ == '__main__':
    result = generate_parquet_data(730)  # 2년치 데이터 생성
    print(result) 

def generate_record_by_type(date, region, data_type, record_id):
    """타입별 레코드 생성"""
    # 월별 계절에 따른 데이터 생성 조절
    month = date.month
    
    # 환경 데이터 가져오기
    environment_data = generate_environment_data(date, region)
    temperature = environment_data['temperature']
    humidity = environment_data['humidity']
    
    # 6월~10월 (여름과 초가을)에만 농업활동 데이터 생성
    is_active_season = month >= 6 and month <= 10
    
    # 레코드 공통 필드
    record = {
        'record_id': record_id,
        'region': region,
        'timestamp': date,
        'data_type': data_type
    }
    
    # 데이터 유형별 필드 생성
    if data_type == 'environment':
        # 환경 데이터는 모든 계절에 생성
        record.update({
            'temperature': temperature,
            'humidity': humidity,
            'co2': round(random.uniform(350, 500), 1),
            'light_intensity': round(random.uniform(0, 100000) * (0.1 if date.hour < 6 or date.hour > 18 else 1), 1)
        })
    
    elif data_type == 'pest' and is_active_season:
        # 해충 관련 데이터 (6월~10월만)
        # 병해충 발생 정도는 온도와 습도에 영향을 받음
        temp_factor = max(0, min(1, (temperature - 15) / 15))  # 15도 이상에서 발생 시작, 30도에서 최대
        humidity_factor = max(0, min(1, (humidity - 50) / 30))  # 50% 이상에서 발생 시작, 80%에서 최대
        
        # 7-8월 고온다습 시기에 병해충 발생 증가
        severity_base = 3
        if month in [7, 8] and temperature > 25 and humidity > 70:
            severity_base = 7
        
        # 최종 심각도 계산 (온도/습도 영향 + 랜덤 변동)
        severity = severity_base * (0.5 * temp_factor + 0.5 * humidity_factor) + np.random.normal(0, 1)
        severity = max(0, min(10, severity))
        
        record.update({
            'pest_type': random.choice(['진딧물', '응애', '흰가루병', '잿빛곰팡이병', '역병']),
            'severity': round(severity),
            'affected_area': round(random.uniform(5, 30 * (severity / 10)), 1),
            'description': f'발생 심각도: {round(severity)}/10'
        })
    
    elif data_type == 'growth' and is_active_season:
        # 생육 관련 데이터 (6월~10월만)
        # 생육 상태는 온도에 영향을 받음
        temp_optimal = 20  # 최적 온도
        temp_effect = max(0, 1 - abs(temperature - temp_optimal) / 15)  # 최적 온도에서 멀어질수록 영향 감소
        
        # 7-8월 성장 최대기
        if month in [7, 8] and temperature > 22 and temperature < 32:
            base_growth = 85
            base_ndvi = 0.75
        elif month in [9, 10]:  # 수확기 근접
            base_growth = 70
            base_ndvi = 0.65
        else:  # 초기 성장기
            base_growth = 60
            base_ndvi = 0.5
        
        # 최종 생육 상태 계산
        growth_status = base_growth * temp_effect + np.random.normal(0, 5)
        growth_status = max(30, min(100, growth_status))
        
        # NDVI 값 계산
        ndvi = base_ndvi * temp_effect + np.random.normal(0, 0.05)
        ndvi = max(0.2, min(0.9, ndvi))
        
        record.update({
            'plant_height': round(random.uniform(30, 150 * (growth_status / 100)), 1),
            'leaf_count': round(random.uniform(5, 20 * (growth_status / 100))),
            'growth_status': round(growth_status),
            'ndvi': round(ndvi, 2)
        })
    
    elif data_type == 'moisture' and is_active_season:
        # 수분 관련 데이터 (6월~10월만)
        # 토양 수분은 최근 강수량과 온도에 영향을 받음
        # 장마철이나 비가 많이 온 경우 수분 함량 높음
        rain_probability = 0.3
        if month == 7:  # 장마철 (7월)
            rain_probability = 0.7
            base_moisture = 55
        elif month == 8:  # 무더위 (8월)
            rain_probability = 0.4
            base_moisture = 45
        else:
            base_moisture = 50
        
        # 비 왔는지 랜덤 결정
        rained_recently = random.random() < rain_probability
        
        # 토양 수분 계산 (비가 왔으면 높고, 온도가 높으면 낮아짐)
        moisture = base_moisture + (10 if rained_recently else 0) - (temperature - 20) * 0.5 + np.random.normal(0, 3)
        moisture = max(20, min(80, moisture))
        
        record.update({
            'soil_moisture': round(moisture, 1),
            'water_stress': round(max(0, 10 - moisture / 8)),
            'irrigation_needed': moisture < 35,
            'last_irrigation': (date - timedelta(days=random.randint(1, 5))).isoformat() if moisture < 40 else None
        })
    
    elif data_type == 'nutrition' and is_active_season:
        # 영양 관련 데이터 (6월~10월만)
        # 기준 영양 상태
        if month in [7, 8]:  # 성장기 영양상태 최대
            base_nutrition = 70
        else:
            base_nutrition = 60
        
        # 최종 영양 상태 계산 (랜덤 변동 추가)
        nutrition_status = base_nutrition + np.random.normal(0, 5)
        nutrition_status = max(30, min(90, nutrition_status))
        
        record.update({
            'n_level': round(random.uniform(30, 80), 1),
            'p_level': round(random.uniform(20, 70), 1),
            'k_level': round(random.uniform(25, 75), 1),
            'nutrition_status': round(nutrition_status),
            'nutrition_deficiency': nutrition_status < 50
        })
    
    elif data_type == 'control' and is_active_season:
        # 제어 관련 데이터 (6월~10월만)
        # 병해충 발생 위험에 따라 제어 조치 결정
        pest_risk = (temperature - 15) * 0.3 + (humidity - 50) * 0.2
        
        # 7-8월에는 방제 조치 증가
        if month in [7, 8] and temperature > 25 and humidity > 70:
            base_actions = 3
            pest_risk += 10
        else:
            base_actions = 1
        
        # 최종 조치 횟수 계산
        action_count = max(0, round(base_actions + pest_risk / 10 + np.random.normal(0, 1)))
        
        # 제어 조치 유형 선택
        action_types = []
        if random.random() < 0.6:
            action_types.append("살충제 살포")
        if random.random() < 0.4:
            action_types.append("살균제 살포")
        if random.random() < 0.3 and humidity > 70:
            action_types.append("환기 조절")
        if random.random() < 0.5 and temperature > 25:
            action_types.append("관수 조절")
        
        # 적어도 하나의 조치는 포함
        if not action_types:
            action_types.append(random.choice(["살충제 살포", "살균제 살포", "관수 조절"]))
        
        record.update({
            'control_type': ", ".join(action_types),
            'action_count': action_count,
            'effectiveness': round(random.uniform(50, 90)),
            'details': f'총 {action_count}회 조치 실행'
        })
    
    else:
        # 환경 데이터가 아니고 활성 시즌이 아닌 경우 None 반환
        return None
    
    return record

def generate_environment_data(timestamp, region):
    """환경 관련 데이터 생성"""
    # 월별 계절에 따른 기온 조절
    month = timestamp.month
    
    # 지역별 기준 온도 설정 (위도에 따른 차이 반영)
    if region == "태안지구":
        base_temp_summer = 28.5  # 서해안 지역 여름 기준 온도
        base_temp_winter = 0.5   # 서해안 지역 겨울 기준 온도
    elif region == "김제지구":
        base_temp_summer = 29.5  # 내륙 지역 여름 기준 온도
        base_temp_winter = -1.0  # 내륙 지역 겨울 기준 온도
    elif region == "밀양지구":
        base_temp_summer = 30.5  # 남부 지역 여름 기준 온도
        base_temp_winter = 1.5   # 남부 지역 겨울 기준 온도
    else:
        base_temp_summer = 29.0  # 기본 여름 기준 온도
        base_temp_winter = 0.0   # 기본 겨울 기준 온도
    
    # 한국의 계절 특성 반영
    if month in [12, 1, 2]:  # 겨울
        # 겨울철 평균 기온: -5 ~ 5도
        base_temp = base_temp_winter
        if month == 1:  # 1월이 가장 추움
            base_temp -= 2
        temp_variation = 4
        # 겨울 일교차 반영
        day_hour_effect = abs(timestamp.hour - 14) / 14 * 8  # 14시를 기준으로 일교차 최대 8도
        season_name = "겨울"
    elif month in [3, 4, 5]:  # 봄
        # 봄 평균 기온: 5 ~ 20도로 점진적 상승
        progress = (month - 3) / 3
        base_temp = base_temp_winter + 5 + progress * 15
        temp_variation = 3
        day_hour_effect = abs(timestamp.hour - 14) / 14 * 7  # 봄 일교차
        season_name = "봄"
    elif month in [6, 7, 8]:  # 여름
        # 7-8월이 가장 더움, 6월은 조금 낮음
        if month == 7 or month == 8:
            base_temp = base_temp_summer
            if month == 8:  # 8월 초가 가장 더움 (한국 폭염기)
                base_temp += (1 if timestamp.day < 15 else 0)
        else:  # 6월
            base_temp = base_temp_summer - 4
        temp_variation = 2
        day_hour_effect = abs(timestamp.hour - 14) / 14 * 5  # 여름 일교차 (다른 계절보다 작음)
        season_name = "여름"
    else:  # 가을 (9, 10, 11)
        # 가을 평균 기온: 점진적 하강 20 ~ 5도
        progress = (11 - month) / 3
        base_temp = base_temp_winter + 5 + progress * 15
        temp_variation = 3
        day_hour_effect = abs(timestamp.hour - 14) / 14 * 7  # 가을 일교차
        season_name = "가을"
    
    # 일 변동 (낮 더움, 밤 추움)
    temperature = base_temp - day_hour_effect + np.random.normal(0, temp_variation)
    
    # 습도: 계절 특성 반영
    if season_name == "여름":
        # 여름에는 습도가 높음 (장마 및 폭염 기간)
        if month == 7:  # 7월 장마기간
            base_humidity = 80
        else:
            base_humidity = 70
    elif season_name == "겨울":
        # 겨울에는 습도가 낮음 (건조함)
        base_humidity = 40
    else:
        # 봄, 가을은 중간 정도
        base_humidity = 60
    
    # 일중 습도 변화 (새벽에 높고 오후에 낮음)
    hour_effect = abs(timestamp.hour - 5) / 19 * 15  # 오전 5시 기준으로 최대 차이 15%
    humidity = base_humidity - hour_effect + np.random.normal(0, 5)
    
    # 값 범위 조정
    temperature = max(-10, min(40, temperature))
    humidity = max(20, min(99, humidity))
    
    return {
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1)
    } 