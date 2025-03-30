/**
 * 재배달력 데이터 관리
 * 작물별 생육과정, 기상재해, 병충해 방제 정보를 관리하는 모듈
 */

// 콩 재배달력 데이터
const soybeanCalendarData = {
    // 생육과정 데이터
    cultivation: [
        {
            category: "생육단계",
            data: [
                { month: 6, text: "유묘, 신장기", color: "success" },
                { month: 7, text: "개화기", color: "success" },
                { month: 8, text: "협성장기", color: "warning" },
                { month: 9, text: "등숙기", color: "warning" },
                { month: 10, text: "수확기", color: "danger" }
            ]
        },
        {
            category: "주요작업",
            data: [
                { month: 6, text: "파종, 초기 제초", color: "success" },
                { month: 7, text: "중기제초", color: "success" },
                { month: 10, text: "수확기", color: "danger" }
            ]
        },
        {
            category: "관리작업",
            data: [
                { month: 7, text: "배수로정비", color: "primary" },
                { month: 8, text: "복주기", color: "primary" }
            ]
        }
    ],
    
    // 기상재해 및 문제점 데이터
    disaster: [
        {
            category: "기상재해",
            data: [
                { month: 6, text: "가뭄", color: "warning" },
                { month: 7, text: "장마", color: "danger" },
                { month: 8, text: "집중호우", color: "danger" },
                { month: 9, text: "태풍, 조기낙엽", color: "warning" }
            ]
        },
        {
            category: "작물피해",
            data: [
                { month: 8, text: "습해, 침수", color: "primary" },
                { month: 9, text: "탈립, 조기낙엽", color: "primary" }
            ]
        }
    ],
    
    // 병충해 방제 데이터
    pest: [
        {
            category: "해충",
            data: [
                { month: 7, text: "나방류", color: "danger" },
                { month: 8, text: "노린재류", color: "danger" },
                { month: 9, text: "노린재류", color: "warning" }
            ]
        },
        {
            category: "병해",
            data: [
                { month: 6, text: "진딧물류", color: "warning" },
                { month: 7, text: "심식충", color: "warning" },
                { month: 8, text: "병해(불마름병 등)", color: "warning" },
                { month: 9, text: "병해(모자이크병 등)", color: "warning" }
            ]
        },
        {
            category: "방제",
            data: [
                { month: 8, text: "방제시기", color: "info" },
                { month: 9, text: "방제시기", color: "info" }
            ]
        }
    ]
};

// 벼 재배달력 데이터
const riceCalendarData = {
    // 생육과정 데이터
    cultivation: [
        {
            category: "생육단계",
            data: [
                { month: 4, text: "육묘기", color: "success" },
                { month: 5, text: "이앙기", color: "success" },
                { month: 6, text: "분얼기", color: "success" },
                { month: 7, text: "유수형성기", color: "warning" },
                { month: 8, text: "출수기", color: "warning" },
                { month: 9, text: "등숙기", color: "warning" },
                { month: 10, text: "수확기", color: "danger" }
            ]
        },
        {
            category: "주요작업",
            data: [
                { month: 4, text: "못자리 준비", color: "success" },
                { month: 5, text: "이앙, 제초제 처리", color: "success" },
                { month: 6, text: "분얼비 시비", color: "primary" },
                { month: 7, text: "중간낙수", color: "primary" },
                { month: 8, text: "이삭비 시비", color: "primary" },
                { month: 10, text: "수확", color: "danger" }
            ]
        },
        {
            category: "관리작업",
            data: [
                { month: 5, text: "물관리", color: "primary" },
                { month: 6, text: "물관리", color: "primary" },
                { month: 7, text: "물관리", color: "primary" },
                { month: 8, text: "물관리", color: "primary" },
                { month: 9, text: "완전물떼기", color: "primary" }
            ]
        }
    ],
    
    // 기상재해 및 문제점 데이터
    disaster: [
        {
            category: "기상재해",
            data: [
                { month: 5, text: "냉해", color: "warning" },
                { month: 6, text: "가뭄", color: "warning" },
                { month: 7, text: "집중호우", color: "danger" },
                { month: 8, text: "태풍", color: "danger" },
                { month: 9, text: "태풍", color: "danger" }
            ]
        },
        {
            category: "작물피해",
            data: [
                { month: 7, text: "침수피해", color: "primary" },
                { month: 8, text: "도복", color: "primary" },
                { month: 9, text: "도복, 수발아", color: "primary" }
            ]
        }
    ],
    
    // 병충해 방제 데이터
    pest: [
        {
            category: "해충",
            data: [
                { month: 6, text: "벼물바구미", color: "warning" },
                { month: 7, text: "멸구류", color: "danger" },
                { month: 8, text: "멸구류, 혹명나방", color: "danger" },
                { month: 9, text: "이삭도열병", color: "warning" }
            ]
        },
        {
            category: "병해",
            data: [
                { month: 7, text: "잎도열병", color: "warning" },
                { month: 8, text: "잎집무늬마름병", color: "warning" },
                { month: 9, text: "깨씨무늬병", color: "warning" }
            ]
        },
        {
            category: "방제",
            data: [
                { month: 6, text: "제1차 방제", color: "info" },
                { month: 7, text: "제2차 방제", color: "info" },
                { month: 8, text: "제3차 방제", color: "info" }
            ]
        }
    ]
};

// 밀 재배달력 데이터
const wheatCalendarData = {
    // 생육과정 데이터
    cultivation: [
        {
            category: "생육단계",
            data: [
                { month: 10, text: "파종기", color: "success" },
                { month: 11, text: "발아기", color: "success" },
                { month: 3, text: "생장기", color: "success" },
                { month: 4, text: "분얼기", color: "warning" },
                { month: 5, text: "출수기", color: "warning" },
                { month: 6, text: "수확기", color: "danger" }
            ]
        },
        {
            category: "주요작업",
            data: [
                { month: 9, text: "파종준비", color: "primary" },
                { month: 10, text: "파종", color: "success" },
                { month: 3, text: "추비", color: "primary" },
                { month: 6, text: "수확", color: "danger" }
            ]
        }
    ],
    
    // 기상재해 및 문제점 데이터
    disaster: [
        {
            category: "기상재해",
            data: [
                { month: 1, text: "동해", color: "danger" },
                { month: 2, text: "동해", color: "danger" },
                { month: 4, text: "가뭄", color: "warning" },
                { month: 5, text: "배수불량", color: "warning" },
                { month: 6, text: "장마", color: "danger" }
            ]
        }
    ],
    
    // 병충해 방제 데이터
    pest: [
        {
            category: "병해",
            data: [
                { month: 4, text: "붉은곰팡이병", color: "warning" },
                { month: 5, text: "흰가루병", color: "warning" },
                { month: 5, text: "녹병", color: "warning" }
            ]
        },
        {
            category: "방제",
            data: [
                { month: 4, text: "방제시기", color: "info" },
                { month: 5, text: "방제시기", color: "info" }
            ]
        }
    ]
};

// 옥수수 재배달력 데이터
const cornCalendarData = {
    // 생육과정 데이터
    cultivation: [
        {
            category: "생육단계",
            data: [
                { month: 4, text: "파종기", color: "success" },
                { month: 5, text: "유묘기", color: "success" },
                { month: 6, text: "생장기", color: "success" },
                { month: 7, text: "개화기", color: "warning" },
                { month: 8, text: "등숙기", color: "warning" },
                { month: 9, text: "수확기", color: "danger" }
            ]
        },
        {
            category: "주요작업",
            data: [
                { month: 4, text: "파종", color: "success" },
                { month: 5, text: "비료공급", color: "primary" },
                { month: 6, text: "김매기, 복토", color: "primary" },
                { month: 9, text: "수확", color: "danger" }
            ]
        }
    ],
    
    // 기상재해 및 문제점 데이터
    disaster: [
        {
            category: "기상재해",
            data: [
                { month: 5, text: "가뭄", color: "warning" },
                { month: 7, text: "집중호우", color: "danger" },
                { month: 8, text: "태풍", color: "danger" }
            ]
        },
        {
            category: "작물피해",
            data: [
                { month: 7, text: "침수피해", color: "primary" },
                { month: 8, text: "도복", color: "primary" }
            ]
        }
    ],
    
    // 병충해 방제 데이터
    pest: [
        {
            category: "해충",
            data: [
                { month: 6, text: "조명나방", color: "warning" },
                { month: 7, text: "조명나방", color: "danger" },
                { month: 7, text: "멸강나방", color: "danger" }
            ]
        },
        {
            category: "병해",
            data: [
                { month: 7, text: "깨씨무늬병", color: "warning" },
                { month: 8, text: "이삭썩음병", color: "warning" }
            ]
        },
        {
            category: "방제",
            data: [
                { month: 6, text: "방제시기", color: "info" },
                { month: 7, text: "방제시기", color: "info" }
            ]
        }
    ]
};

// 지역별 재배 시기 조정 매핑 (월 단위)
const regionOffsets = {
    // 기본값 (전국 평균)
    all: {
        offset: 0
    },
    // 김제지구 - 중부지방에 위치, 표준 시기
    gimje: {
        offset: 0
    },
    // 밀양지구 - 남부지방에 위치, 약간 빠른 시기
    miryang: {
        offset: -1
    },
    // 태안지구 - 서해안 지방, 표준보다 조금 늦은 시기
    taean: {
        offset: 1
    }
};

// 재배달력 데이터 관리 객체
const CalendarDataManager = {
    // 작물별 데이터 저장
    data: {
        soybean: soybeanCalendarData,
        rice: riceCalendarData,
        wheat: wheatCalendarData,
        corn: cornCalendarData
    },
    
    // 작물과 카테고리에 따른 데이터 가져오기
    getData: function(crop, category) {
        if (!this.data[crop]) {
            console.error(`${crop} 작물에 대한 데이터가 없습니다.`);
            return [];
        }
        
        if (!this.data[crop][category]) {
            console.error(`${crop} 작물의 ${category} 카테고리에 대한 데이터가 없습니다.`);
            return [];
        }
        
        return this.data[crop][category];
    },
    
    // 모든 카테고리의 데이터 가져오기
    getAllData: function(crop) {
        if (!this.data[crop]) {
            console.error(`${crop} 작물에 대한 데이터가 없습니다.`);
            return null;
        }
        
        return this.data[crop];
    },
    
    // 사용 가능한 작물 목록 가져오기
    getAvailableCrops: function() {
        return Object.keys(this.data);
    },
    
    // 사용 가능한 카테고리 목록 가져오기
    getAvailableCategories: function(crop) {
        if (!this.data[crop]) {
            console.error(`${crop} 작물에 대한 데이터가 없습니다.`);
            return [];
        }
        
        return Object.keys(this.data[crop]);
    },
    
    // 지역에 따른 데이터 조정
    getRegionalData: function(crop, category, region = 'all') {
        const data = this.getData(crop, category);
        if (!data || !regionOffsets[region]) {
            return data;
        }
        
        const offset = regionOffsets[region].offset;
        
        // 오프셋이 0이면 조정할 필요 없음
        if (offset === 0) {
            return data;
        }
        
        // 각 카테고리 데이터의 월 정보 조정
        return data.map(categoryData => {
            return {
                category: categoryData.category,
                data: categoryData.data.map(item => {
                    // 실제 월 계산 (1-12 범위 유지)
                    let adjustedMonth = item.month + offset;
                    if (adjustedMonth < 1) adjustedMonth = 12 + adjustedMonth;
                    if (adjustedMonth > 12) adjustedMonth = adjustedMonth - 12;
                    
                    return {
                        ...item,
                        month: adjustedMonth
                    };
                })
            };
        });
    },
    
    // 지역 목록 가져오기
    getAvailableRegions: function() {
        return Object.keys(regionOffsets);
    },
    
    // 지역 정보 가져오기
    getRegionInfo: function(region) {
        return regionOffsets[region] || regionOffsets.all;
    }
};

// 전역 객체로 노출
window.CalendarDataManager = CalendarDataManager; 