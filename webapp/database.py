import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# Use a service account.
cred = credentials.Certificate('./aiot-nuguna-03687aeaa9e6.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()


def get_device(d_id):
    device = db.collection('device').document(d_id).get()
    if device.exists:
        return device.to_dict()

def create_device(d_id):
    doc_ref = db.collection('device').document(d_id)
    if not doc_ref.get().exists:
        device = {d_id: {
            'id': d_id,
            'is_running': False,
            'manufacture_date': '20221213',
            'sensor': []
        }}
        doc_ref.set(device)


def upload_sensor(d_id, sensor):
    doc_ref = db.collection('device').document(d_id)
    sensor['update_time'] = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    doc_ref.update({'sensor': firestore.ArrayUnion([sensor])})




