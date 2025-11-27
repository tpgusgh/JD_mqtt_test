import ssl
import json
import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "mqtt-web.mieung.kr"
MQTT_PORT = 443
TOPIC = "echo/record"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code:", rc)
    if rc == 0:
        print("MQTT 연결 성공!")

def on_publish(client, userdata, mid):
    print("메시지 발행 완료:", mid)

def main():
    client = mqtt.Client(transport="websockets")

    # Cloudflare SSL 설정
    client.tls_set(
        cert_reqs=ssl.CERT_NONE,
        tls_version=ssl.PROTOCOL_TLSv1_2,
    )
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_publish = on_publish

    print("MQTT 브로커 연결 중...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()
    time.sleep(1)

    # === 테스트할 주문번호 입력 ===
    name = "cafe"

    payload = {
        "name": name
    }

    print("📤 발행 payload:", payload)

    client.publish(TOPIC, json.dumps(payload), qos=0)

    print("완료 메시지 전송됨.")
    time.sleep(2)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
