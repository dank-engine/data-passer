from google.transit import gtfs_realtime_pb2
import time
import requests

lines = ['BDBN', 'BDBR', 'BDRW', 'BDVL', 'BNBD', 'BNBR', 'BNDB', 'BNFG', 'BNSH', 'BRBD', 'BRBN', 'BRCA', 'BRCL', 'BRDB', 'BRFG', 'BRGY', 'BRIP', 'BRNA', 'BRRP', 'BRRW', 'BRSH', 'BRSP', 'BRVL', 'CABR', 'CACL', 'CAIP', 'CARW', 'CASP', 'CLBR', 'CLDB', 'CLSH', 'DBBN', 'DBBR', 'DBCL', 'DBDB', 'FGBN', 'FGBR', 'GYBR', 'IPBR', 'IPCA', 'IPDB', 'IPFG', 'IPNA', 'IPRP', 'IPRW', 'NABR', 'NAIP', 'NASP', 'RBUS', 'RPBR', 'RPCL', 'RPIP', 'RPSP', 'RWBD', 'RWBR', 'RWCA', 'RWIP', 'RWNA', 'RWRP', 'SHBN', 'SHBR', 'SHCL', 'SHSP', 'SPBR', 'SPCA', 'SPDB', 'SPNA', 'SPRP', 'VLBD', 'VLBR', 'VLDB']


def get_train_data(chosen_lines):
    """
    Takes a list of lines and returns the data neccesary to interact with.

    Parameters:
        chosen_lines(list): List of Lines to get data for.

    Returns:
        [current_time, (trip_id, route_id, stop_id, stopped, arrival_time, arrival_delay, departure_time, departure_delay, stop_sequence), ...]

    """
    data = []
    vehicle_data = []
    output = []   

    # Gather the Protobuffer
    feed = gtfs_realtime_pb2.FeedMessage()
    current_time = round(time.time())
    r = requests.get("https://gtfsrt.api.translink.com.au/Feed/SEQ")
    feed.ParseFromString(r.content)

    # Begin Stripping of Data
    message = feed.entity
    for entity in message:
        append = True
        if entity.trip_update.trip.HasField("schedule_relationship"):
            append = False
        elif entity.trip_update.trip.route_id[0:4] not in chosen_lines:
            append = False

        if not entity.HasField("trip_update") and entity.vehicle.trip.route_id[0:4] in chosen_lines:
            vehicle_data.append(entity)

        if append:
            data.append(entity)
        
    
    output.append(current_time)
    train_stopped = {}
    for entry in vehicle_data:
        trip_id = entry.vehicle.trip.trip_id

        current_status = entry.vehicle.current_status
        train_stopped[trip_id] = current_status



    for entry in data:
        stop_info = entry.trip_update.stop_time_update[0]

        trip_id = entry.trip_update.trip.trip_id
        route_id = entry.trip_update.trip.route_id
        stop_id = stop_info.stop_id
        arrival_time = stop_info.arrival.time
        departure_time = stop_info.departure.time
        stop_sequence = stop_info.stop_sequence

        departure_delay = stop_info.departure.delay
        arrival_delay = stop_info.arrival.delay

        stopped = train_stopped.get(trip_id)
        
        packet = (trip_id, route_id, stop_id, stopped, arrival_time, arrival_delay, departure_time, departure_delay, stop_sequence)
        output.append(packet)


    return output