from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

API_KEY = <key>

def set_control(device, control, value):
    command = ['/usr/bin/v4l2-ctl', '-d', f'/dev/video{device}', '--set-ctrl', f'{control}={value}']
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return {'message': 'Command executed successfully', 'control': control, 'value': value}
    except subprocess.CalledProcessError as e:
        return {'error': 'Command failed', 'detail': e.stderr.strip()}

def get_control(device, control):
    command = ['/usr/bin/v4l2-ctl', '-d', f'/dev/video{device}', '--get-ctrl', control]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        search = re.search(rf'{control}: (\d+)', result.stdout)
        if search:
            return {control: int(search.group(1))}
        else:
            return {'error': f'{control} value not found'}
    except subprocess.CalledProcessError as e:
        return {'error': 'Failed to retrieve value', 'detail': e.stderr.strip()}

def verify_api_key(request):
    api_key = request.headers.get('Authorization')
    return api_key == API_KEY

@app.route('/camera-control', methods=['POST'])
def control_camera():
    if not verify_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    device = data.get('device')
    controls = data.get('controls')

    if device is None or controls is None:
        return jsonify({'error': 'Missing data'}), 400

    results = {}
    for control, value in controls.items():
        result = set_control(device, control, value)
        results[control] = result

    return jsonify(results), 200

@app.route('/list-controls', methods=['GET'])
def list_controls():
    if not verify_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401

    device = request.args.get('device', default=0, type=int)
    command = ['/usr/bin/v4l2-ctl', '-d', f'/dev/video{device}', '-l']
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        controls = {}
        for line in result.stdout.splitlines():
            match = re.search(r'(\w+)\s+0x[\da-fA-F]{8}\s+\((\w+)\)\s+:\s+min=(\d+)\s+max=(\d+)\s+step=(\d+)\s+default=(\d+)\s+value=(\d+)', line)
            if match:
                control_name, control_type = match.group(1), match.group(2)
                if control_type == 'bool':
                    value = match.group(7) == '1'
                else:
                    value = int(match.group(7))
                control_details = {
                    'type': control_type,
                    'min': int(match.group(3)),
                    'max': int(match.group(4)),
                    'step': int(match.group(5)),
                    'default': int(match.group(6)),
                    'value': value
                }
                controls[control_name] = control_details
        return jsonify(controls)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to list controls', 'detail': str(e.stderr.strip())})


@app.route('/camera-status', methods=['GET'])
def camera_status():
    if not verify_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401

    device = request.args.get('device', default=0, type=int)
    controls = request.args.getlist('controls')  # e.g., 'brightness', 'contrast', ...

    if not controls:
        return jsonify({'error': 'No controls specified'}), 400

    results = {}
    for control in controls:
        result = get_control(device, control)
        results[control] = result

    return jsonify(results), 200

if __name__ == '__main__':
    app.run()