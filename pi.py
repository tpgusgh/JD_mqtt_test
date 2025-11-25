# mqtt_rooms_publish_test.py

import json
import ssl
import paho.mqtt.client as mqtt

BROKER = "mqtt-web.mieung.kr"
PORT = 443
TOPIC = "echo/save"

client = mqtt.Client(transport="websockets")

client.tls_set(
    cert_reqs=ssl.CERT_NONE,
    tls_version=ssl.PROTOCOL_TLSv1_2,
)
client.tls_insecure_set(True)

def on_connect(client, userdata, flags, rc):
    print("🔗 Connected! rc =", rc)
    if rc == 0:
        data = {
            "rooms": ["카페", "3-1반", "회의실", "강당", "승환이 얼굴"]
        }
        payload = json.dumps(data, ensure_ascii=False)
        client.publish(TOPIC, payload)
        print("📤 MQTT 발행 완료 →", payload)
    else:
        print("❌ 연결 실패")

def on_log(client, userdata, level, buf):
    print("📝 LOG:", buf)

client.on_connect = on_connect
client.on_log = on_log

print("🔄 MQTT WebSocket 연결 시도...")
client.connect(BROKER, PORT, 60)
client.loop_forever()