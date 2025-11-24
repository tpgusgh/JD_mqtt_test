import json
import ssl
import paho.mqtt.client as mqtt

BROKER = "mqtt-web.mieung.kr"
PORT = 443
TOPIC = "stock/topic"

# MQTT over WebSocket + TLS
client = mqtt.Client(transport="websockets")

# --- Cloudflare 호환 SSL 설정 ---
client.tls_set(
    cert_reqs=ssl.CERT_NONE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(True)

# Subprotocol 지정 (Cloudflare는 요구함)
client.ws_set_options(path="/mqtt", headers=None)

def on_connect(client, userdata, flags, rc):
    print("🔗 Connected! RC =", rc)
    if rc == 0:
        print("✅ MQTT WebSocket 연결 성공")
        client.publish(TOPIC, json.dumps({"water": "LOW"}))
    else:
        print("❌ 연결 실패")

def on_log(client, userdata, level, buf):
    print("📝 LOG:", buf)

client.on_connect = on_connect
client.on_log = on_log

print("🔄 MQTT WebSocket 연결 시도 중...")
client.connect(BROKER, PORT, 60)

client.loop_forever()
