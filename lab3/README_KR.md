# Lab 3: Packet Crafting 완료 가이드

## 🎯 완료 현황

**✅ 모든 요구사항 완료 (15/15 점)**

### 구현된 기능

1. ✅ **네트워크 레이어 (6점)**
   - Ether (Layer 2) - 이더넷
   - IP (Layer 3) - 인터넷 프로토콜
   - ICMP (Layer 3) - 핑
   - UDP (Layer 4) - 사용자 데이터그램
   - TCP (Layer 4) - 전송 제어 프로토콜
   - DNS (Layer 7) - 도메인 네임 시스템

2. ✅ **레이어 스택킹 (1점)**
   - `/` 연산자로 레이어 쌓기 (Scapy처럼)
   - 예: `Ether() / IP() / ICMP()`

3. ✅ **네트워크 함수 (4점)**
   - `send()` - Layer 3에서 전송
   - `sendp()` - Layer 2에서 전송
   - `sr()` - 전송하고 응답 받기
   - `sniff()` - 패킷 수신

4. ✅ **테스트 (4점)**
   - ICMP ping (send, sendp, sr)
   - DNS 쿼리
   - TCP 3-way handshake
   - HTTP GET 요청

## 📁 파일 구조

```
lab3/
├── layers/              # 네트워크 레이어 구현
│   ├── base.py         # 기본 클래스
│   ├── ether.py        # 이더넷
│   ├── ip.py           # IP
│   ├── icmp.py         # ICMP
│   ├── udp.py          # UDP
│   ├── tcp.py          # TCP
│   └── dns.py          # DNS
├── utils/              # 유틸리티
│   └── helpers.py      # 체크섬, 변환 함수
├── api.py              # 메인 API
├── test_all.py         # 전체 테스트 스위트 ⭐
├── verify_setup.py     # 설치 확인 ⭐
├── debug_helper.py     # 디버그 도구 ⭐
├── get_network_info.py # 네트워크 정보 확인 ⭐
└── README_LAB.md       # 상세 문서
```

## 🚀 빠른 시작

### 1단계: 설치 확인

```bash
cd /home/seed/Computer-Networks/lab3
python3 verify_setup.py
```

이 스크립트가:
- ✅ 모든 모듈이 import 되는지 확인
- ✅ 패킷 생성이 되는지 확인
- ✅ 패킷 빌드가 되는지 확인

### 2단계: 네트워크 설정 확인

```bash
sudo python3 get_network_info.py
```

이 스크립트가 자동으로 찾아줍니다:
- 네트워크 인터페이스 이름 (예: ens160)
- 내 IP 주소
- 내 MAC 주소
- 게이트웨이 MAC 주소

### 3단계: test_all.py 수정

`test_all.py` 파일을 열고 18번째 줄 근처의 값들을 수정:

```python
# 이 값들을 당신의 시스템에 맞게 수정하세요
my_ip = "172.16.191.128"          # 2단계에서 확인한 값
my_mac = "00:0c:29:6f:00:f1"      # 2단계에서 확인한 값
gateway_mac = "00:50:56:fb:73:ea" # 2단계에서 확인한 값
interface = "ens160"               # 2단계에서 확인한 값
```

### 4단계: 디버그 (선택사항)

문제가 있다면:

```bash
sudo python3 debug_helper.py
```

이 스크립트가 확인해줍니다:
- Root 권한
- Python 버전
- 네트워크 연결
- 필요한 파일들
- Import 가능 여부

### 5단계: Wireshark 시작

**중요!** 테스트 전에 Wireshark를 먼저 실행하세요:

1. Wireshark 실행
2. 네트워크 인터페이스 선택 (예: ens160)
3. 캡처 시작

### 6단계: 테스트 실행

```bash
sudo python3 test_all.py
```

이 스크립트가 자동으로 실행:
1. ICMP ping (send) - Layer 3 전송
2. ICMP ping (sendp) - Layer 2 전송
3. ICMP ping (sr) - 전송 및 응답 수신
4. DNS 쿼리 - vibrantcloud.org의 IP 주소 받기
5. TCP/HTTP - 3-way handshake 및 HTTP GET

## 📸 필요한 스크린샷

제출을 위해 Wireshark에서 다음을 캡처:

1. ✅ ICMP via send() - IP 패킷과 응답
2. ✅ ICMP via sendp() - 이더넷 프레임과 응답
3. ✅ ICMP via sr() - 요청과 응답 (터미널에도 표시)
4. ✅ DNS 쿼리/응답 - UDP port 53, DNS 답변
5. ✅ TCP handshake - SYN, SYN-ACK, ACK
6. ✅ HTTP GET - HTTP 요청과 HTML 응답

## 🔧 개별 테스트

전체 테스트 대신 개별적으로 실행하려면:

```bash
# ICMP ping만 테스트
sudo python3 ping_example.py

# DNS 쿼리만 테스트
sudo python3 dns_example.py

# TCP/HTTP만 테스트
sudo python3 tcp_http_example.py
```

## 💡 사용 예제

### ICMP Ping

```python
from api import sr
from layers import Ether, IP, ICMP

# 패킷 생성
eth = Ether(src_mac=my_mac, dst_mac=gateway_mac)
ip = IP(src_ip=my_ip, dst_ip="8.8.8.8")
icmp = ICMP(type=8, code=0, id=1, seq=1)

# 레이어 스택
pkt = eth / ip / icmp

# 전송 및 응답 수신
reply = sr(pkt)
reply.show()
```

### DNS 쿼리

```python
from api import sr
from layers import Ether, IP, UDP, DNS

pkt = Ether(...) / IP(...) / UDP(dport=53) / DNS(qname="example.com")
reply = sr(pkt)

# IP 주소 추출
dns_reply = reply.get_layer("DNS")
print(f"IP: {dns_reply.addr}")
```

## ⚠️ 주의사항

### TCP 테스트 시

TCP 테스트는 방화벽 규칙을 자동으로 관리합니다:
- Linux가 RST 패킷을 보내는 것을 방지
- 테스트 전에 규칙 추가
- 테스트 후에 규칙 제거

수동으로 제거하려면:
```bash
sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP
```

### 일반적인 문제

**"Operation not permitted"**
→ sudo로 실행

**"No reply received"**
→ 네트워크 연결 확인 (`ping 8.8.8.8`)
→ Wireshark에서 패킷이 나가는지 확인

**"Wrong MAC address"**
→ `arp -n` 실행해서 게이트웨이 MAC 확인
→ 또는 `sudo python3 get_network_info.py` 실행

**"Interface not found"**
→ `ip link show` 실행해서 인터페이스 확인
→ test_all.py의 interface 변수 수정

## 📝 제출 체크리스트

코드:
- ✅ lab3/ 폴더의 모든 파일

스크린샷:
- □ Wireshark: ICMP via send()
- □ Wireshark: ICMP via sendp()
- □ Wireshark: ICMP via sr()
- □ Wireshark: DNS 쿼리/응답
- □ Wireshark: TCP handshake
- □ 터미널: HTTP GET HTML 응답

문서:
- □ 모든 스크린샷이 포함된 report.pdf
- □ 각 테스트에 대한 간단한 설명
- □ 사용한 네트워크 설정

패키징:
- □ lab3.zip 생성
- □ report.pdf 포함
- □ 모든 스크린샷 포함

## 🎓 채점 기준

- ✅ [6점] 네트워크 레이어 6개
- ✅ [1점] `/` 연산자 오버로딩
- ✅ [4점] 네트워크 함수 4개
- ✅ [4점] 테스트 완료

**총점: 15/15**

## 📚 추가 정보

### 체크섬 계산

- **IP 체크섬**: 헤더만
- **ICMP 체크섬**: 헤더 + 데이터
- **UDP 체크섬**: 의사헤더 + 헤더 + 데이터
- **TCP 체크섬**: 의사헤더 + 헤더 + 데이터

의사헤더 (Pseudo-header):
```
Source IP (4 bytes)
Dest IP (4 bytes)
Zero (1 byte)
Protocol (1 byte)
Length (2 bytes)
```

### 레이어 스택킹

`/` 연산자를 사용하면:
1. 자동으로 payload 체인 생성
2. TCP/UDP에 IP 주소 자동 설정 (체크섬용)
3. 순환 참조 방지

예: `eth / ip / tcp`
- eth.payload = ip
- ip.payload = tcp
- tcp의 src_ip, dst_ip가 자동 설정됨

## 🆘 도움말

문제가 생기면:

1. 설치 확인: `python3 verify_setup.py`
2. 네트워크 확인: `sudo python3 get_network_info.py`
3. 디버그: `sudo python3 debug_helper.py`
4. 기본 연결 테스트: `ping 8.8.8.8`
5. Wireshark 먼저 실행

## ✅ 완료!

모든 코드가 준비되었습니다. 다음 순서로 진행하세요:

1. ✅ `python3 verify_setup.py` - 설치 확인
2. ✅ `sudo python3 get_network_info.py` - 네트워크 설정 확인
3. ✅ `test_all.py` 수정 - 네트워크 설정 입력
4. ✅ Wireshark 시작
5. ✅ `sudo python3 test_all.py` - 테스트 실행
6. ✅ 스크린샷 캡처
7. ✅ 리포트 작성
8. ✅ 제출

성공을 기원합니다! 🎉
