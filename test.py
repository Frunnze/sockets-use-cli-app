from datetime import datetime, timedelta
import time

# Save the current datetime
start_time = datetime.now()

end_time = datetime.now().isoformat()
print(datetime.fromisoformat(end_time))
