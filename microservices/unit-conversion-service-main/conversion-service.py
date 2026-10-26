from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

PORT = 6901
app = Flask(__name__)
CORS(app)

'''
Conversions:
lbs = kgs * 2.20462
kgs = lbs * 0.45359
oz = g * 0.03527
g = oz * 28.3495
'''

# Multiply by CONVERSION_CONSTANT to convert from {from_unit} to {to_unit}
CONVERSION_CONSTANT = {
    "kg_to_lb": 2.2046226218,
    "lb_to_kg": 0.45359237,
    "g_to_oz": 0.0352739619,
    "oz_to_g": 28.3495231
}

# Create convert unit endpoint
@app.route("/convert-unit", methods=["POST"])
def convert_unit():
    data = request.get_json()

    # data validation
    if not data:
        return jsonify({"error": "Missing input." }), 400
    keys = ['value', 'from_unit', 'to_unit']
    for key in keys:
        if key not in data:
            return jsonify({"error": "Missing " + key + "." }), 400

    val = data['value']
    from_unit = data['from_unit'].lower()
    to_unit = data['to_unit'].lower()

    # Get the CONVERSION_CONSTANT
    key = f"{from_unit}_to_{to_unit}"
    if key in CONVERSION_CONSTANT:
        res = val * CONVERSION_CONSTANT[key]
    else:
        return jsonify({
            "ok": False,
            "error": {"code": "TYPE_ERROR", "message": f"Conversion from_unit {from_unit} to {to_unit} is invalid."}
            }), 400
    
    return jsonify(         
        {
        "original_val": val,
        "converted_val": res,
        "rounded_val": round(res, 2),
        "from_unit": from_unit,
        "to_unit": to_unit,
        "message": "Converted successfully!"
        }
    ), 200


@app.route("/convert-time", methods=["POST"])
def convert_time():
    data = request.get_json()

    if not data:
        return jsonify({"ok": False, "error": "Missing JSON body"}), 400

    twelve_hr_time = data.get("twelveHourTime")
    twentyfour_hr_time = data.get("twentyFourHourTime")

    if (twelve_hr_time is None and twentyfour_hr_time is None) or (twelve_hr_time and twentyfour_hr_time):
        return jsonify({
            "ok": False,
            "error": "Input should be: twelveHourTime OR twentyFourHourTime, not both or neither."
        }), 400
    
    if twelve_hr_time is None:
        mode = "24 to 12"
    else:
        mode = "12 to 24"
    
    try:
        match mode:
            case "12 to 24":
                dt = datetime.strptime(twelve_hr_time.upper(), "%I:%M %p")
                result = dt.strftime("%H:%M")
                return jsonify({
                    "ok": True,
                    "twelveHourTime": twelve_hr_time,
                    "twentyFourHourTime": result
                }), 200
            
            case "24 to 12":
                dt = datetime.strptime(twentyfour_hr_time, "%H:%M")
                result = dt.strftime("%I:%M %p").lstrip("0")

                return jsonify({
                    "ok": True,
                    "twelveHourTime": result,
                    "twentyFourHourTime": twentyfour_hr_time
                }), 200     
    except:
        return jsonify({
            "ok": False,
            "error": "Invalid time format"
        }), 400


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
    