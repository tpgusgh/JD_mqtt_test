import paho.mqtt.client as mqtt
import ssl

# 설정값
MQTT_HOST = "aibrokerweb.mieung.kr"
MQTT_PORT = 443
MQTT_TOPIC = "grad/project"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ 브로커 연결 성공: {MQTT_HOST}")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 [{MQTT_TOPIC}] 토픽 구독 중... ESP32의 신호를 기다립니다.")
    else:
        print(f"❌ 연결 실패 (코드: {rc})")

def on_message(client, userdata, msg):
    # ESP32가 보낸 메시지 출력
    print(f"🔔 [ESP32 전송 데이터]: {msg.payload.decode()}")

# 웹소켓 모드로 클라이언트 생성
client = mqtt.Client(transport="websockets")

# Cloudflare Tunnel(HTTPS/WSS)을 통과하기 위한 SSL 설정
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message

print("🔗 클라우드플레어 터널 접속 시도 중...")
try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()
except Exception as e:
    print(f"⚠️ 에러 발생: {e}")