import minimalmodbus
import sys
import json
import uuid
sys.path.append("../Shared")

from api import Api

# Check if the system is Linux
is_linux = sys.platform == 'linux'

if is_linux:
    # Configure the Modbus instrument
    addr = 240
    instrument = minimalmodbus.Instrument("/dev/serial0", addr)
    # Adjust the port and slave address as needed
    instrument.serial.baudrate = 9600  # Adjust the baudrate as needed
    instrument.mode = minimalmodbus.MODE_RTU  # RTU mode
    instrument.debug = False  # Enable or Disable debugging

    # Define the Modbus holding register address to read
    holding_register_address = 0  # Adjust the address as needed
    num_registers = 2  # Adjust the number of registers as needed

    try:
        val = instrument.read_registers(holding_register_address, num_registers, functioncode=3)

        print(f"Holding Registers {holding_register_address}, 1 value: {val}")

        out_dict_status = {
            "Holding_Register_Value": val, 
            "SampleTime": "GetUTCDate()",
            "LocalTime": "GetUTCDate()"  # Added LocalTime field
        }

        out_dict_history = {
            "Holding_Register_Value": val, 
            "SampleTime": "GetUTCDate()",
            "LocalTime": "GetUTCDate()",  # Added LocalTime field
            "UId": 0,  # Provide appropriate default value for UId
            "DeviceId": 0  # Provide appropriate default value for DeviceId
        }

        file_name = sys.argv[1] if len(sys.argv) > 1 else "sensor-1.json"
        with open(file_name, 'r') as f:
            input_data = json.load(f)

        if input_data.get("save"):
            if "sql" in input_data:
                cols = input_data["sql"]["cols"]
                if cols:
                    for obj in cols:
                        out_dict_history[obj["name"]] = obj["value"]
                        out_dict_status[obj["name"]] = obj["value"]
            status_table_name = input_data["sql"]["statusTable"]
            history_table_name = input_data["sql"]["historyTable"]
            res_status = Api.post("db/Insert/" + status_table_name, out_dict_status)
            res_history = Api.post("db/Insert/" + history_table_name, out_dict_history)
            device = {"Id": out_dict_status["DeviceId"], "Status": "ok", "SampleTime": "GetUTCDate()", "UpdatedOn": "GetUTCDate()"}
            res_device = Api.post("db/Update/Device", device)
            print("Status Table:", res_status.text)
            print("History Table:", res_history.text)
            print("Device Table:", res_device.text)

    except Exception as e:
        print(f"Error: {e}")

else:
    # Dummy data
    model_status = {
        "UId": 739,
        "Guid": str(uuid.uuid4()),
        "DeviceId": 1947,
        "SampleTime": "GetUTCDate()",
        "SunshineHours": 0.0,
        "Radiation": 0.0,
        "Power": 0.0,
        "Temperature": 0.0,
        "LocalTime": "GetUTCDate()"  
    }
    model_history = {
        "Guid": str(uuid.uuid4()),
        "SampleTime": "GetUTCDate()",
        "SunshineHours": 0.0,
        "Radiation": 0.0,
        "Power": 0.0,
        "Temperature": 0.0,
        "LocalTime": "GetUTCDate()",  
        "UId": 739,  
        "DeviceId": 1947  
    }
    res_status = Api.post("db/Insert/RadiationSensorStatus", model_status)
    res_history = Api.post("db/Insert/RadiationSensorHistory", model_history)
    print("Status Table:", res_status.text)
    print("History Table:", res_history.text)
