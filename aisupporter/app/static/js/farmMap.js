/**
 * FarmMap - 노지AI재배관리시스템을 위한 농장 지도 라이브러리
 * 버전: 1.0.0
 * 트랜스포머 컨소시엄
 */

class FarmMap {
  /**
   * FarmMap 생성자
   * @param {string} containerId - 맵을 표시할 컨테이너 요소의 ID
   * @param {Object} options - 초기화 옵션
   * @param {number} options.width - 맵의 너비 (픽셀)
   * @param {number} options.height - 맵의 높이 (픽셀)
   * @param {string} options.mapImage - 맵 배경 이미지 URL (선택사항)
   * @param {string} options.defaultZoneColor - 기본 구역 색상 (선택사항)
   * @param {Object} options.legendConfig - 범례 설정 (선택사항)
   */
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    
    if (!this.container) {
      console.error(`FarmMap: 컨테이너 요소 "${containerId}"를 찾을 수 없습니다.`);
      return;
    }
    
    this.options = Object.assign({
      width: 800,
      height: 600,
      mapImage: null,
      defaultZoneColor: '#4CAF50',
      showLegend: false,
      legendConfig: {
        position: 'bottom-right',
        title: '상태 범례'
      }
    }, options);
    
    // 내부 상태 초기화
    this.zones = [];
    this.markers = [];
    this.sensors = [];
    this.eventHandlers = {};
    this.selectedZone = null;
    
    // 맵 생성
    this._initializeMap();
  }
  
  /**
   * 맵 초기화
   * @private
   */
  _initializeMap() {
    // 컨테이너 스타일 설정
    this.container.style.position = 'relative';
    this.container.style.width = `${this.options.width}px`;
    this.container.style.height = `${this.options.height}px`;
    this.container.style.overflow = 'hidden';
    this.container.style.backgroundColor = '#f8f9fa';
    this.container.style.border = '1px solid #dee2e6';
    this.container.style.borderRadius = '0.5rem';
    
    // 맵 컨테이너 생성
    this.mapContainer = document.createElement('div');
    this.mapContainer.className = 'farm-map-canvas';
    this.mapContainer.style.position = 'absolute';
    this.mapContainer.style.top = '0';
    this.mapContainer.style.left = '0';
    this.mapContainer.style.width = '100%';
    this.mapContainer.style.height = '100%';
    
    // 배경 이미지가 있으면 추가
    if (this.options.mapImage) {
      this.mapContainer.style.backgroundImage = `url(${this.options.mapImage})`;
      this.mapContainer.style.backgroundSize = 'cover';
      this.mapContainer.style.backgroundPosition = 'center';
    }
    
    // 구역 레이어 생성
    this.zoneLayer = document.createElement('div');
    this.zoneLayer.className = 'farm-map-zone-layer';
    this.zoneLayer.style.position = 'absolute';
    this.zoneLayer.style.top = '0';
    this.zoneLayer.style.left = '0';
    this.zoneLayer.style.width = '100%';
    this.zoneLayer.style.height = '100%';
    this.zoneLayer.style.pointerEvents = 'none';
    
    // 마커 레이어 생성
    this.markerLayer = document.createElement('div');
    this.markerLayer.className = 'farm-map-marker-layer';
    this.markerLayer.style.position = 'absolute';
    this.markerLayer.style.top = '0';
    this.markerLayer.style.left = '0';
    this.markerLayer.style.width = '100%';
    this.markerLayer.style.height = '100%';
    this.markerLayer.style.pointerEvents = 'none';
    
    // 인터랙션 레이어 생성
    this.interactionLayer = document.createElement('div');
    this.interactionLayer.className = 'farm-map-interaction-layer';
    this.interactionLayer.style.position = 'absolute';
    this.interactionLayer.style.top = '0';
    this.interactionLayer.style.left = '0';
    this.interactionLayer.style.width = '100%';
    this.interactionLayer.style.height = '100%';
    this.interactionLayer.style.zIndex = '10';
    
    // 컨트롤 레이어 생성
    this.controlLayer = document.createElement('div');
    this.controlLayer.className = 'farm-map-control-layer';
    this.controlLayer.style.position = 'absolute';
    this.controlLayer.style.top = '10px';
    this.controlLayer.style.right = '10px';
    this.controlLayer.style.zIndex = '20';
    
    // 레이어 추가
    this.mapContainer.appendChild(this.zoneLayer);
    this.mapContainer.appendChild(this.markerLayer);
    this.mapContainer.appendChild(this.interactionLayer);
    this.container.appendChild(this.mapContainer);
    this.container.appendChild(this.controlLayer);
    
    // 범례가 활성화되어 있으면 추가
    if (this.options.showLegend) {
      this._addLegend();
    }
    
    // 이벤트 핸들러 등록
    this._registerEventListeners();
  }
  
  /**
   * 맵에 범례 추가
   * @private
   */
  _addLegend() {
    const legend = document.createElement('div');
    legend.className = 'farm-map-legend';
    legend.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    legend.style.borderRadius = '4px';
    legend.style.padding = '10px';
    legend.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
    legend.style.position = 'absolute';
    
    // 범례 위치 설정
    switch (this.options.legendConfig.position) {
      case 'top-right':
        legend.style.top = '10px';
        legend.style.right = '10px';
        break;
      case 'top-left':
        legend.style.top = '10px';
        legend.style.left = '10px';
        break;
      case 'bottom-left':
        legend.style.bottom = '10px';
        legend.style.left = '10px';
        break;
      case 'bottom-right':
      default:
        legend.style.bottom = '10px';
        legend.style.right = '10px';
        break;
    }
    
    // 범례 제목
    const title = document.createElement('div');
    title.textContent = this.options.legendConfig.title || '상태 범례';
    title.style.fontWeight = 'bold';
    title.style.marginBottom = '5px';
    title.style.borderBottom = '1px solid #eee';
    title.style.paddingBottom = '5px';
    
    legend.appendChild(title);
    
    // 범례 항목
    const items = [
      { color: '#4CAF50', label: '정상' },
      { color: '#FFC107', label: '주의' },
      { color: '#F44336', label: '경고' }
    ];
    
    items.forEach(item => {
      const itemEl = document.createElement('div');
      itemEl.style.display = 'flex';
      itemEl.style.alignItems = 'center';
      itemEl.style.marginTop = '5px';
      
      const colorBox = document.createElement('div');
      colorBox.style.width = '16px';
      colorBox.style.height = '16px';
      colorBox.style.backgroundColor = item.color;
      colorBox.style.marginRight = '8px';
      colorBox.style.borderRadius = '3px';
      
      const label = document.createElement('div');
      label.textContent = item.label;
      label.style.fontSize = '0.875rem';
      
      itemEl.appendChild(colorBox);
      itemEl.appendChild(label);
      legend.appendChild(itemEl);
    });
    
    this.container.appendChild(legend);
  }
  
  /**
   * 이벤트 리스너 등록
   * @private
   */
  _registerEventListeners() {
    this.interactionLayer.addEventListener('click', (e) => {
      const rect = this.container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // 클릭한 위치에 있는 구역 확인
      const clickedZone = this._findZoneAt(x, y);
      
      if (clickedZone) {
        this.selectZone(clickedZone.id);
        this._triggerEvent('zoneClick', clickedZone);
      } else {
        this.clearSelection();
        this._triggerEvent('mapClick', { x, y });
      }
    });
  }
  
  /**
   * 특정 좌표에 있는 구역 찾기
   * @param {number} x - X 좌표
   * @param {number} y - Y 좌표
   * @returns {Object|null} - 발견된 구역 또는 null
   * @private
   */
  _findZoneAt(x, y) {
    // 간단한 구현: 첫 번째로 일치하는 구역 반환
    // 실제 구현에서는 구역의 형태에 따라 더 복잡한 알고리즘 필요
    return this.zones.find(zone => {
      const el = document.getElementById(`zone-${zone.id}`);
      if (!el) return false;
      
      const rect = el.getBoundingClientRect();
      const containerRect = this.container.getBoundingClientRect();
      
      const zoneX = rect.left - containerRect.left;
      const zoneY = rect.top - containerRect.top;
      
      return (
        x >= zoneX &&
        x <= zoneX + rect.width &&
        y >= zoneY &&
        y <= zoneY + rect.height
      );
    }) || null;
  }
  
  /**
   * 이벤트 발생
   * @param {string} eventName - 이벤트 이름
   * @param {Object} data - 이벤트 데이터
   * @private
   */
  _triggerEvent(eventName, data) {
    if (this.eventHandlers[eventName]) {
      this.eventHandlers[eventName].forEach(handler => handler(data));
    }
  }
  
  /**
   * 구역 추가
   * @param {Object} zoneData - 구역 데이터
   * @param {string} zoneData.id - 구역 ID
   * @param {string} zoneData.name - 구역 이름
   * @param {number} zoneData.x - 구역 X 좌표 (%)
   * @param {number} zoneData.y - 구역 Y 좌표 (%)
   * @param {number} zoneData.width - 구역 너비 (%)
   * @param {number} zoneData.height - 구역 높이 (%)
   * @param {string} zoneData.color - 구역 색상 (선택사항)
   * @param {string} zoneData.status - 구역 상태 (normal, warning, danger) (선택사항)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addZone(zoneData) {
    const zone = Object.assign({
      color: this.options.defaultZoneColor,
      status: 'normal'
    }, zoneData);
    
    // 기존 구역 중복 체크
    const existingZoneIndex = this.zones.findIndex(z => z.id === zone.id);
    if (existingZoneIndex !== -1) {
      this.zones[existingZoneIndex] = zone;
      this._updateZoneElement(zone);
    } else {
      this.zones.push(zone);
      this._createZoneElement(zone);
    }
    
    return this;
  }
  
  /**
   * 구역 추가 (한 번에 여러 구역)
   * @param {Array<Object>} zonesData - 구역 데이터 배열
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addZones(zonesData) {
    zonesData.forEach(zoneData => this.addZone(zoneData));
    return this;
  }
  
  /**
   * 구역 HTML 요소 생성
   * @param {Object} zone - 구역 데이터
   * @private
   */
  _createZoneElement(zone) {
    const zoneEl = document.createElement('div');
    zoneEl.id = `zone-${zone.id}`;
    zoneEl.className = 'farm-map-zone';
    zoneEl.dataset.zoneId = zone.id;
    
    // 구역 스타일 설정
    zoneEl.style.position = 'absolute';
    zoneEl.style.left = `${zone.x}%`;
    zoneEl.style.top = `${zone.y}%`;
    zoneEl.style.width = `${zone.width}%`;
    zoneEl.style.height = `${zone.height}%`;
    zoneEl.style.pointerEvents = 'all';
    zoneEl.style.cursor = 'pointer';
    
    // 상태에 따른 색상 설정
    this._applyZoneStatus(zoneEl, zone);
    
    // 구역 이름 추가
    const nameEl = document.createElement('div');
    nameEl.className = 'farm-map-zone-name';
    nameEl.textContent = zone.name;
    nameEl.style.position = 'absolute';
    nameEl.style.bottom = '5px';
    nameEl.style.left = '5px';
    nameEl.style.color = 'white';
    nameEl.style.textShadow = '0 0 2px rgba(0,0,0,0.7)';
    nameEl.style.fontSize = '0.9rem';
    nameEl.style.fontWeight = 'bold';
    
    zoneEl.appendChild(nameEl);
    this.zoneLayer.appendChild(zoneEl);
  }
  
  /**
   * 구역 HTML 요소 업데이트
   * @param {Object} zone - 구역 데이터
   * @private
   */
  _updateZoneElement(zone) {
    const zoneEl = document.getElementById(`zone-${zone.id}`);
    if (!zoneEl) return;
    
    // 위치 및 크기 업데이트
    zoneEl.style.left = `${zone.x}%`;
    zoneEl.style.top = `${zone.y}%`;
    zoneEl.style.width = `${zone.width}%`;
    zoneEl.style.height = `${zone.height}%`;
    
    // 상태 업데이트
    this._applyZoneStatus(zoneEl, zone);
    
    // 이름 업데이트
    const nameEl = zoneEl.querySelector('.farm-map-zone-name');
    if (nameEl) {
      nameEl.textContent = zone.name;
    }
  }
  
  /**
   * 구역 상태 스타일 적용
   * @param {HTMLElement} zoneEl - 구역 HTML 요소
   * @param {Object} zone - 구역 데이터
   * @private
   */
  _applyZoneStatus(zoneEl, zone) {
    let backgroundColor, borderColor, opacity;
    
    switch (zone.status) {
      case 'warning':
        backgroundColor = '#FFC107';
        borderColor = '#FF9800';
        opacity = 0.5;
        break;
      case 'danger':
        backgroundColor = '#F44336';
        borderColor = '#D32F2F';
        opacity = 0.5;
        break;
      case 'normal':
      default:
        backgroundColor = zone.color || this.options.defaultZoneColor;
        borderColor = this._darkenColor(backgroundColor, 20);
        opacity = 0.4;
        break;
    }
    
    zoneEl.style.backgroundColor = backgroundColor;
    zoneEl.style.border = `2px solid ${borderColor}`;
    zoneEl.style.opacity = opacity;
    zoneEl.style.borderRadius = '4px';
    zoneEl.style.transition = 'all 0.3s ease';
  }
  
  /**
   * 색상 어둡게 만들기
   * @param {string} color - 색상 코드
   * @param {number} percent - 어둡게 할 퍼센트
   * @returns {string} - 변환된 색상 코드
   * @private
   */
  _darkenColor(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;
    
    return '#' + (
      0x1000000 +
      (R < 0 ? 0 : R) * 0x10000 +
      (G < 0 ? 0 : G) * 0x100 +
      (B < 0 ? 0 : B)
    ).toString(16).slice(1);
  }
  
  /**
   * 마커 추가
   * @param {Object} markerData - 마커 데이터
   * @param {string} markerData.id - 마커 ID
   * @param {string} markerData.type - 마커 유형 (sensor, point, etc.)
   * @param {number} markerData.x - 마커 X 좌표 (%)
   * @param {number} markerData.y - 마커 Y 좌표 (%)
   * @param {string} markerData.icon - 마커 아이콘 (boxicons 이름)
   * @param {string} markerData.color - 마커 색상 (선택사항)
   * @param {Object} markerData.data - 마커 추가 데이터 (선택사항)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addMarker(markerData) {
    const marker = Object.assign({
      color: '#2196F3',
      icon: 'bx-map-pin'
    }, markerData);
    
    // 기존 마커 중복 체크
    const existingMarkerIndex = this.markers.findIndex(m => m.id === marker.id);
    if (existingMarkerIndex !== -1) {
      this.markers[existingMarkerIndex] = marker;
      this._updateMarkerElement(marker);
    } else {
      this.markers.push(marker);
      this._createMarkerElement(marker);
    }
    
    return this;
  }
  
  /**
   * 마커 추가 (한 번에 여러 마커)
   * @param {Array<Object>} markersData - 마커 데이터 배열
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addMarkers(markersData) {
    markersData.forEach(markerData => this.addMarker(markerData));
    return this;
  }
  
  /**
   * 마커 HTML 요소 생성
   * @param {Object} marker - 마커 데이터
   * @private
   */
  _createMarkerElement(marker) {
    const markerEl = document.createElement('div');
    markerEl.id = `marker-${marker.id}`;
    markerEl.className = `farm-map-marker farm-map-marker-${marker.type}`;
    markerEl.dataset.markerId = marker.id;
    
    // 마커 스타일 설정
    markerEl.style.position = 'absolute';
    markerEl.style.left = `${marker.x}%`;
    markerEl.style.top = `${marker.y}%`;
    markerEl.style.transform = 'translate(-50%, -50%)';
    markerEl.style.width = '32px';
    markerEl.style.height = '32px';
    markerEl.style.backgroundColor = marker.color;
    markerEl.style.borderRadius = '50%';
    markerEl.style.display = 'flex';
    markerEl.style.alignItems = 'center';
    markerEl.style.justifyContent = 'center';
    markerEl.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    markerEl.style.cursor = 'pointer';
    markerEl.style.transition = 'all 0.3s ease';
    markerEl.style.zIndex = '5';
    
    // 아이콘 추가
    const iconEl = document.createElement('i');
    iconEl.className = `bx ${marker.icon}`;
    iconEl.style.color = 'white';
    iconEl.style.fontSize = '18px';
    
    markerEl.appendChild(iconEl);
    
    // 툴팁 추가 (있는 경우)
    if (marker.tooltip) {
      markerEl.title = marker.tooltip;
    }
    
    // 클릭 이벤트 리스너 추가
    markerEl.addEventListener('click', (e) => {
      e.stopPropagation();
      this._triggerEvent('markerClick', marker);
    });
    
    // 호버 효과
    markerEl.addEventListener('mouseenter', () => {
      markerEl.style.transform = 'translate(-50%, -50%) scale(1.15)';
    });
    
    markerEl.addEventListener('mouseleave', () => {
      markerEl.style.transform = 'translate(-50%, -50%) scale(1)';
    });
    
    this.markerLayer.appendChild(markerEl);
  }
  
  /**
   * 마커 HTML 요소 업데이트
   * @param {Object} marker - 마커 데이터
   * @private
   */
  _updateMarkerElement(marker) {
    const markerEl = document.getElementById(`marker-${marker.id}`);
    if (!markerEl) return;
    
    // 위치 업데이트
    markerEl.style.left = `${marker.x}%`;
    markerEl.style.top = `${marker.y}%`;
    
    // 색상 업데이트
    markerEl.style.backgroundColor = marker.color;
    
    // 아이콘 업데이트
    const iconEl = markerEl.querySelector('i');
    if (iconEl) {
      iconEl.className = `bx ${marker.icon}`;
    }
    
    // 툴팁 업데이트
    if (marker.tooltip) {
      markerEl.title = marker.tooltip;
    }
  }
  
  /**
   * 센서 데이터 추가
   * @param {Object} sensorData - 센서 데이터
   * @param {string} sensorData.id - 센서 ID
   * @param {string} sensorData.type - 센서 유형 (temperature, humidity, etc.)
   * @param {number} sensorData.x - 센서 X 좌표 (%)
   * @param {number} sensorData.y - 센서 Y 좌표 (%)
   * @param {number} sensorData.value - 센서 값
   * @param {string} sensorData.unit - 센서 단위 (°C, %, etc.)
   * @param {string} sensorData.status - 센서 상태 (normal, warning, danger)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addSensor(sensorData) {
    // 센서 유형에 따른 아이콘 설정
    let icon, color;
    
    switch (sensorData.type) {
      case 'temperature':
        icon = 'bx-sun';
        color = '#FF9800';
        break;
      case 'humidity':
        icon = 'bx-droplet';
        color = '#2196F3';
        break;
      case 'soil_moisture':
        icon = 'bx-water';
        color = '#4CAF50';
        break;
      case 'light':
        icon = 'bx-bulb';
        color = '#FFC107';
        break;
      default:
        icon = 'bx-chip';
        color = '#9E9E9E';
        break;
    }
    
    // 상태에 따른 색상 조정
    if (sensorData.status === 'warning') {
      color = '#FFC107';
    } else if (sensorData.status === 'danger') {
      color = '#F44336';
    }
    
    // 툴팁 생성
    const tooltip = `${sensorData.name || sensorData.type}: ${sensorData.value}${sensorData.unit || ''}`;
    
    // 마커로 추가
    const markerData = {
      id: `sensor-${sensorData.id}`,
      type: 'sensor',
      x: sensorData.x,
      y: sensorData.y,
      icon: icon,
      color: color,
      tooltip: tooltip,
      data: sensorData
    };
    
    this.addMarker(markerData);
    
    // 센서 목록에 추가
    const existingSensorIndex = this.sensors.findIndex(s => s.id === sensorData.id);
    if (existingSensorIndex !== -1) {
      this.sensors[existingSensorIndex] = sensorData;
    } else {
      this.sensors.push(sensorData);
    }
    
    return this;
  }
  
  /**
   * 센서 데이터 추가 (한 번에 여러 센서)
   * @param {Array<Object>} sensorsData - 센서 데이터 배열
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  addSensors(sensorsData) {
    sensorsData.forEach(sensorData => this.addSensor(sensorData));
    return this;
  }
  
  /**
   * 구역 선택
   * @param {string} zoneId - 선택할 구역 ID
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  selectZone(zoneId) {
    // 이전 선택 해제
    this.clearSelection();
    
    // 선택한 구역 찾기
    const zone = this.zones.find(z => z.id === zoneId);
    if (!zone) return this;
    
    // 선택한 구역 강조
    const zoneEl = document.getElementById(`zone-${zoneId}`);
    if (zoneEl) {
      zoneEl.style.opacity = '0.7';
      zoneEl.style.border = '2px solid #FFF';
      zoneEl.style.boxShadow = '0 0 10px rgba(0,0,0,0.3)';
    }
    
    this.selectedZone = zone;
    this._triggerEvent('zoneSelect', zone);
    
    return this;
  }
  
  /**
   * 구역 선택 해제
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  clearSelection() {
    if (this.selectedZone) {
      const zoneEl = document.getElementById(`zone-${this.selectedZone.id}`);
      if (zoneEl) {
        this._applyZoneStatus(zoneEl, this.selectedZone);
      }
    }
    
    this.selectedZone = null;
    return this;
  }
  
  /**
   * 구역 상태 업데이트
   * @param {string} zoneId - 구역 ID
   * @param {string} status - 새 상태 (normal, warning, danger)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  updateZoneStatus(zoneId, status) {
    const zoneIndex = this.zones.findIndex(z => z.id === zoneId);
    if (zoneIndex === -1) return this;
    
    this.zones[zoneIndex].status = status;
    this._updateZoneElement(this.zones[zoneIndex]);
    
    return this;
  }
  
  /**
   * 센서 값 업데이트
   * @param {string} sensorId - 센서 ID
   * @param {number} value - 새 센서 값
   * @param {string} status - 새 상태 (normal, warning, danger) (선택사항)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  updateSensorValue(sensorId, value, status) {
    const sensorIndex = this.sensors.findIndex(s => s.id === sensorId);
    if (sensorIndex === -1) return this;
    
    // 센서 데이터 업데이트
    this.sensors[sensorIndex].value = value;
    if (status) {
      this.sensors[sensorIndex].status = status;
    }
    
    // 마커 업데이트
    this.addSensor(this.sensors[sensorIndex]);
    
    return this;
  }
  
  /**
   * 이벤트 리스너 등록
   * @param {string} eventName - 이벤트 이름
   * @param {Function} handler - 이벤트 핸들러
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  on(eventName, handler) {
    if (!this.eventHandlers[eventName]) {
      this.eventHandlers[eventName] = [];
    }
    
    this.eventHandlers[eventName].push(handler);
    return this;
  }
  
  /**
   * 이벤트 리스너 제거
   * @param {string} eventName - 이벤트 이름
   * @param {Function} handler - 제거할 이벤트 핸들러 (생략 시 모든 핸들러 제거)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  off(eventName, handler) {
    if (!this.eventHandlers[eventName]) return this;
    
    if (handler) {
      this.eventHandlers[eventName] = this.eventHandlers[eventName].filter(h => h !== handler);
    } else {
      this.eventHandlers[eventName] = [];
    }
    
    return this;
  }
  
  /**
   * 맵 크기 조정
   * @param {number} width - 새 너비 (픽셀)
   * @param {number} height - 새 높이 (픽셀)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  resize(width, height) {
    this.options.width = width;
    this.options.height = height;
    
    this.container.style.width = `${width}px`;
    this.container.style.height = `${height}px`;
    
    return this;
  }
  
  /**
   * 맵 초기화 (모든 데이터 제거)
   * @returns {FarmMap} - 메소드 체이닝을 위한 FarmMap 인스턴스
   */
  clear() {
    // HTML 요소 제거
    this.zoneLayer.innerHTML = '';
    this.markerLayer.innerHTML = '';
    
    // 데이터 초기화
    this.zones = [];
    this.markers = [];
    this.sensors = [];
    this.selectedZone = null;
    
    return this;
  }
  
  /**
   * 맵 제거
   */
  destroy() {
    // 이벤트 리스너 제거
    this.eventHandlers = {};
    
    // HTML 요소 제거
    this.container.innerHTML = '';
    
    // 참조 제거
    this.zones = null;
    this.markers = null;
    this.sensors = null;
    this.selectedZone = null;
    this.options = null;
    this.container = null;
  }
}

// 모듈 내보내기 (브라우저 및 CommonJS 환경 모두 지원)
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = FarmMap;
} else {
  window.FarmMap = FarmMap;
} 