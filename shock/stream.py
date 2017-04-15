from core import Shock

shock = Shock()
shock.start()
shock.subscribe('data_stream', 'data_collection')
shock.digest()
shock.close()
