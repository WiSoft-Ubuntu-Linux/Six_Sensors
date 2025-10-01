import time
import adafruit_dht
import board
import psycopg2
from psycopg2 import sql
import datetime
import serial

dht_device = adafruit_dht.DHT22(board.D4)

UART_BUS = None  
def pm_init():
  global UART_BUS
  try:
      UART_BUS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
      UART_BUS.flush()  
      print("UART connection successful!")
  except serial.SerialException as e:
      print(f"UART connection failed: {e}")
  except Exception as e:
      print(f"An unexpected error occurred: {e}")

DB_URL = "postgresql://neondb_owner:npg_0dwXPaM5mELt@ep-crimson-pond-a1wep87d-pooler.ap-southeast-1.aws.neon.tech/classdata?sslmode=require&channel_binding=require"
conn = None
def sql_init():
  global conn
  try:
    conn = psycopg2.connect(DB_URL)
    print("Database connection successful!")
  except psycopg2.OperationalError as e:
    print(f"Database connection failed: {e}")


def read_dht_data():
  if not dht_device:
    return None, None
  try:
    temperature = dht_device.temperature
    humidity = dht_device.humidity
        
    if humidity is not None and temperature is not None:
      return temperature, humidity
  except RuntimeError as error:
    print(f"DHT22 reading error: {error.args[0]}")
    return None, None
  
def read_pm_data():
  if not UART_BUS or not UART_BUS.is_open:
    return None, None
  try:
    UART_BUS.reset_input_buffer()
    data = UART_BUS.read(32)
    if len(data) == 32 and data[0] == 0x42 and data[1] == 0x4d:
      pm2_5 = (data[12] << 8) | data[13]
      pm10 = (data[14] << 8) | data[15]
      return pm2_5, pm10
    else:
      return None, None
  except Exception as e:
    print(f"PM Sensor reading error: {e}")
    return None, None


def insert_to_db(temp, hum, pm2_5, pm10, conn):
  try:
    cur = conn.cursor()
    now = datetime.datetime.now()
    insert_query = sql.SQL("""
      INSERT INTO sensor_data (room_id, room_name, temperature, humidity, pm2_5, pm10, timestamp)
      VALUES (%s, %s, %s, %s, %s, %s, %s)
      """)
      
    cur.execute(insert_query, (1, 504, temp, hum, pm2_5, pm10, now.strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()

    print("data has been successfully stored in the database.")

    current_time = datetime.datetime.now().isoformat()
        
  except (Exception, psycopg2.Error) as error:
    print(f"PostgreSQL error: {error}")
        
  finally:
    if conn:
      cur.close()
      conn.close()

try:
  while True:
    if conn is None or conn.closed != 0:
      sql_init()
    if UART_BUS is None or not UART_BUS.is_open:
      pm_init()
    temp, hum = read_dht_data()
    pm2_5, pm10 = read_pm_data()
    print(f"temp: {temp}, hum: {hum}, pm2_5: {pm2_5}, pm10: {pm10}")
    while True:
      if temp is not None and hum is not None and pm2_5 is not None and pm10 is not None:
        insert_to_db(temp, hum, pm2_5, pm10, conn)
        break
      else:
        print("Retrying to read sensor data...")
        time.sleep(2)
        if conn is None or conn.closed != 0:
          sql_init()
        if UART_BUS is None or not UART_BUS.is_open:
          pm_init()
        temp, hum = read_dht_data()
        pm2_5, pm10 = read_pm_data()  

    print("---")
    time.sleep(300) 

except KeyboardInterrupt:
  print("End")

finally:
  if UART_BUS and UART_BUS.is_open:
    UART_BUS.close()
  if dht_device:
    dht_device.exit()