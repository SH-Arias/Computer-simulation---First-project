import random
import simpy
import numpy

SEED = 42 #Generator Seed
#Uncontrolled Variables
CARS_ARRIVAL = [0, 45] #Cars can arrive to the first queue (for fastening) every [0, 90] minutes

#Decision Variables
CARS = 12 #Number of cars to be considered for the simulation
F_TIME = [10, 20] #The Fastening process can last between [15, 30] minutes
I_TIME = [25, 50] #The Inspection process can last between [60, 120] minutes
R_TIME = [60, 210] #The Reparation process can last between [60, 180] minutes
technicians_capacity  = 2
repairmen_capacity = 4

#Performance variables
F_QUEUE = 0 #Queue for the Fasten process
F_QUEUE_VALUES = numpy.array([])
MAX_F_QUEUE = 0
F_WAITING_TIME = numpy.array([])
I_QUEUE = 0 #Queue for the Inspect process
I_QUEUE_VALUES = numpy.array([])
MAX_I_QUEUE = 0
I_WAITING_TIME = numpy.array([])
R_QUEUE = 0 #Queue for the Repair process
R_QUEUE_VALUES = numpy.array([])
MAX_R_QUEUE = 0
R_WAITING_TIME = numpy.array([])

SIMULATION_TIME = 0

#Events definitions for the simulation
def car_repair_shop(env, number, counterTechnicians, counterRepairmen):
        
    #Events
    for i in range(number):

        car_name = 'Car %02d' % i

        f = car(env, car_name, counterTechnicians)
        env.process(f)
        arrival_time = random.uniform(CARS_ARRIVAL[0], CARS_ARRIVAL[1])
        yield env.timeout(arrival_time) #Yield, returns an iterable object


#Car Events definition. Remember, the car itself is a process within the simulation!
def car(env, name, technicians):
    #The car arrives to the Car Repair Shop
    f_arrival = env.now
    print('%7.2f'%(env.now), "For fastening, arrives ", name)

    #STATISTICS
    global F_QUEUE #Arrival/Fastening Queue
    global F_QUEUE_VALUES
    global MAX_F_QUEUE
    global F_WAITING_TIME

    with technicians.request() as req:
        #Wait until the car is fastened
        F_QUEUE += 1
        F_QUEUE_VALUES = numpy.append(F_QUEUE_VALUES, F_QUEUE)
        if F_QUEUE > MAX_F_QUEUE:
            MAX_F_QUEUE = F_QUEUE
        
        result = yield req
        F_QUEUE = F_QUEUE - 1
        F_QUEUE_VALUES = numpy.append(F_QUEUE_VALUES, F_QUEUE)
        waiting_time = env.now - f_arrival
        F_WAITING_TIME = numpy.append(F_WAITING_TIME, waiting_time)

        print('%7.2f'%(env.now), name, " waits for fastening ", waiting_time)

        fastening_time = random.uniform(F_TIME[0], F_TIME[1])
        yield env.timeout(fastening_time)

        print('%7.2f'%(env.now), "Fastening finished for ", name)

    #The car arrives for inspection
    i_arrival = env.now
    print('%7.2f'%(env.now), "For inspection, arrives ", name)

    #STATISTICS
    global I_QUEUE #Inspection Queue
    global I_QUEUE_VALUES
    global MAX_I_QUEUE
    global I_WAITING_TIME

    with technicians.request() as req_t, repairmen.request() as req_r:
        #Wait until the car is inspected
        I_QUEUE += 1
        I_QUEUE_VALUES = numpy.append(I_QUEUE_VALUES, I_QUEUE)
        if I_QUEUE > MAX_I_QUEUE:
            MAX_I_QUEUE = I_QUEUE

        result_1 = yield req_t
        result_2 = yield req_r
        I_QUEUE = I_QUEUE - 1
        I_QUEUE_VALUES = numpy.append(I_QUEUE_VALUES, I_QUEUE)
        waiting_time = env.now - i_arrival
        I_WAITING_TIME = numpy.append(I_WAITING_TIME, waiting_time)

        print('%7.2f'%(env.now), name, " waits for inspection ", waiting_time)

        inspection_time = random.uniform(I_TIME[0], I_TIME[1])
        yield env.timeout(inspection_time)

        print('%7.2f'%(env.now), "Inspection finished for ", name)

    #The car arrives for reparation
    r_arrival = env.now
    print('%7.2f'%(env.now), "For reparation, arrives ", name)

    #STATISTICS
    global R_QUEUE #Arrival/Fastening Queue
    global R_QUEUE_VALUES
    global MAX_R_QUEUE
    global R_WAITING_TIME

    with repairmen.request() as req:
        #Wait until the car is repaired
        R_QUEUE += 1
        R_QUEUE_VALUES = numpy.append(R_QUEUE_VALUES, R_QUEUE)
        if R_QUEUE > MAX_R_QUEUE:
                MAX_R_QUEUE = R_QUEUE

        result = yield req
        R_QUEUE = R_QUEUE - 1
        R_QUEUE_VALUES = numpy.append(R_QUEUE_VALUES, R_QUEUE)
        waiting_time = env.now - r_arrival
        R_WAITING_TIME = numpy.append(R_WAITING_TIME, waiting_time)

        print('%7.2f'%(env.now), name, " waits for reparation ", waiting_time)

        reparation_time = random.uniform(R_TIME[0], R_TIME[1])
        yield env.timeout(reparation_time)

        print('%7.2f'%(env.now), "Reparation finished for ", name)
        


#Simulation start
print("Car Repair Shop")
random.seed(SEED)
env = simpy.Environment()

#Process start and execution
technicians = simpy.Resource(env, capacity = technicians_capacity)
repairmen = simpy.Resource(env, capacity = repairmen_capacity)
env.process(car_repair_shop(env, CARS, technicians, repairmen))
env.run()

SIMULATION_TIME = env.now

average_waiting_time_for_fastening = numpy.mean(F_WAITING_TIME)
average_waiting_time_for_inspection = numpy.mean(I_WAITING_TIME)
average_waiting_time_for_reparation = numpy.mean(R_WAITING_TIME)

average_waiting_time = average_waiting_time_for_fastening + average_waiting_time_for_inspection + average_waiting_time_for_reparation

#Tiempo de espera
WAITING_TIME = numpy.array([])

for i in range(12):
    WAITING_TIME = numpy.append(WAITING_TIME, F_WAITING_TIME[i]+I_WAITING_TIME[i]+R_WAITING_TIME[i])

print("Max Queue for Fastening ", MAX_F_QUEUE)
print("Average Queue for Fastening ",'%7.2f'%(numpy.mean(F_QUEUE_VALUES)))
print("Average waiting time for Fastening ",'%7.2f'%(average_waiting_time_for_fastening))

print("Max Queue for Inspection ", MAX_I_QUEUE)
print("Average Queue for Inspection ",'%7.2f'%(numpy.mean(I_QUEUE_VALUES)))
print("Average waiting time for Inspection ",'%7.2f'%(average_waiting_time_for_inspection))

print("Max Queue for Reparation ", MAX_R_QUEUE)
print("Average Queue for Reparation ",'%7.2f'%(numpy.mean(R_QUEUE_VALUES)))
print("Average waiting time for Reparation ",'%7.2f'%(average_waiting_time_for_reparation))

print("Average waiting time ",'%7.2f'%(average_waiting_time))

print("Simulation time = ",'%7.2f'%(SIMULATION_TIME))

#EoF