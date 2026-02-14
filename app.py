import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'factory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class Worker(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))

class Workstation(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    type = db.Column(db.String(100))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    worker_id = db.Column(db.String(10), db.ForeignKey('worker.id'))
    workstation_id = db.Column(db.String(10), db.ForeignKey('workstation.id'))
    event_type = db.Column(db.String(50)) 
    confidence = db.Column(db.Float)
    count = db.Column(db.Integer, default=0)

# --- Seeding ---
def seed_data():
    if Worker.query.first() is None:
        workers = [Worker(id=f"W{i}", name=f"Worker {i}") for i in range(1, 7)]
        stations = [Workstation(id=f"S{i}", type="Assembly Station") for i in range(1, 7)]
        db.session.add_all(workers + stations)
        
        # Initial dummy events to show metrics immediately
        for i in range(1, 7):
            db.session.add(Event(timestamp=datetime.utcnow(), worker_id=f"W{i}", workstation_id=f"S{i}", 
                                 event_type="working", confidence=0.98, count=0))
            db.session.add(Event(timestamp=datetime.utcnow(), worker_id=f"W{i}", workstation_id=f"S{i}", 
                                 event_type="product_count", confidence=0.99, count=10))
        db.session.commit()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ingest', methods=['POST'])
def ingest():
    data = request.json
    new_event = Event(
        timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '')),
        worker_id=data['worker_id'],
        workstation_id=data['workstation_id'],
        event_type=data['event_type'],
        confidence=data.get('confidence', 0),
        count=data.get('count', 0)
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"message": "Event recorded"}), 201

@app.route('/api/metrics')
def get_metrics():
    events = Event.query.all()
    if not events: return jsonify({})
    
    df = pd.DataFrame([{
        'worker': e.worker_id, 'station': e.workstation_id,
        'type': e.event_type, 'count': e.count, 'time': e.timestamp
    } for e in events])

    # Metric Logic:
    # 1. Total Units
    total_units = int(df[df['type'] == 'product_count']['count'].sum())
    
    # 2. Worker Metrics
    worker_list = []
    for w_id in df['worker'].unique():
        w_df = df[df['worker'] == w_id]
        working_count = len(w_df[w_df['type'] == 'working'])
        idle_count = len(w_df[w_df['type'] == 'idle'])
        total_logs = working_count + idle_count
        util = (working_count / total_logs * 100) if total_logs > 0 else 0
        
        worker_list.append({
            "id": w_id,
            "units": int(w_df[w_df['type'] == 'product_count']['count'].sum()),
            "utilization": f"{util:.1f}%"
        })

    # 3. Factory Average
    avg_util = sum([float(w['utilization'].replace('%','')) for w in worker_list]) / len(worker_list) if worker_list else 0

    return jsonify({
        "factory": {"total_units": total_units, "avg_utilization": f"{avg_util:.1f}%"},
        "workers": worker_list
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
   # This allows Render to tell the app which port to use
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
