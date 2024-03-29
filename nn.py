"""
This may not be NEAT, and instead just an evolution system that is inspired from things I've read and seen.
Ideally much simpler to understand.
"""
import numpy as np
import flappy_game
import copy

# , 'p0_x', 'p0_y', 'p1_x', 'p2_y'
inputs = ['player_x', 'player_y', 'pipe1_loc', 'pipe2_loc']
outputs = ['Up']

POPULATION = 100
BREED_PROBABILITY = 0.75
MUTATE_PROBABILITY = 0.5


def sigmoid(x):
    return 2/(1+np.exp(-4.9*x))-1


class Pool:
    def __init__(self):
        # With this system of genomes I no longer need to use weird randomness stuff
        self.genomes = []
        self.generation = 0
        # The current genome/species is in relation to the original arrays
        self.genome_index = 0

        self.gen_max_fitness = 0
        self.max_fitness = 0
        self.current_frame = 0


class Genome:
    def __init__(self):
        self.fitness = 0
        self.network = None
        self.max_h_neurons = 1
        self.max_connections = 2


class Network:
    def __init__(self):
        # We can identify inputs and outputs based on the number of inputs and outputs in the system
        self.units = []


class Connection:
    def __init__(self):
        self.starting_unit = None
        self.weight = 0.0
        self.ending_unit = None


class Unit:
    def __init__(self):
        self.incoming_connections = []
        self.value = 0.0
        # Placeholder enabled until we may need it (with biases)
        self.enabled = True


def initialise_pool():
    """
    Fills a new pool with a set of genomes, where those genomes are filled randomly with different networks at random.
    """
    global pool
    pool = Pool()
    for i in range(POPULATION):
        genom = basic_genome()
        pool.genomes.append(genom)
    return pool


def basic_genome():
    """
    Generates a new genome with a random network of units (not fully connected).
    """
    genom = Genome()
    genom.network = generate_network(genom)
    return genom


def get_inputs():
    # inputs = ['player_x', 'player_y', 'pipe1_loc', 'pipe2_loc']
    player_x = fb_game.player.rect.center[0]
    player_y = fb_game.player.rect.center[1]
    pipe1_loc = fb_game.pipe1.rect.bottom
    pipe2_loc = fb_game.pipe2.rect.top
    return np.array([player_x, player_y, pipe1_loc, pipe2_loc])


def generate_network(genome):
    network = Network()

    for inp in range(len(inputs)):
        network.units.append(Unit())

    for out in range(len(outputs)):
        network.units.append(Unit())

    num_h_units = int(np.ceil(np.random.random()*genome.max_h_neurons))
    num_connections = int(np.ceil(np.random.random()*genome.max_connections))

    for i in range(num_h_units):
        network.units.append(Unit())

    while num_connections > 0:
        conn = Connection
        b = np.sqrt(6) / np.sqrt(num_h_units)
        conn.weight = np.random.uniform(-b, b)  # sample from that thing before
        # We don't want to start a connection from an output node
        conn.starting_unit = network.units[np.random.randint(0, len(network.units)-len(outputs))]
        # We don't want to end a connection from an input node
        ending_index = np.random.randint(len(inputs), len(network.units))
        conn.ending_unit = network.units[ending_index]
        if conn.starting_unit == conn.ending_unit:
            continue
        else:
            network.units[ending_index].incoming_connections.append(conn)
            num_connections -= 1

    return network


def evaluate_network(network, inputs):
    for i in range(len(inputs)):
        network.units[i].value = inputs[i]
        # print(f'in {inputs[i]}')

    # TODO change this
    for unit in network.units:
        w_sum = 0
        for conn in unit.incoming_connections:
            other = conn.starting_unit
            w_sum += conn.weight * other.value

        if len(unit.incoming_connections) > 0:
            unit.value = sigmoid(w_sum)
    # print([x.value for x in network.units])
    button_outputs = {'Up': False, 'Down': False}
    for o in range(0, len(outputs)):
        # print(network.units[-(len(outputs)-o)].value)
        if network.units[-(len(outputs)-o)].value > 0:
            button_outputs[outputs[o]] = True
        else:
            button_outputs[outputs[o]] = False

    return button_outputs


def evaluate_current_genome(genome):
    inputs = get_inputs()

    controller = evaluate_network(genome.network, inputs)

    if controller['Up'] and controller['Down']:
        controller['Up'] = False
        controller['Down'] = False

    return controller


def new_generation():
    print(f'Max fitness gen {pool.generation}: {pool.max_fitness}')

    # Reducing genomes for later breeding/copying
    pool.genomes = sorted(pool.genomes, key=lambda x: x.fitness)[::-1]
    pool.gen_max_fitness = pool.genomes[0].fitness
    cutoff = len(pool.genomes) * 0.5  # Taking x% of top genomes
    pool.genomes = pool.genomes[:int(cutoff)]

    # Populating
    children = []
    for i, genom in enumerate(pool.genomes):
        dupe_count = (genom.fitness / pool.gen_max_fitness) * (POPULATION * 0.4)
        # print(f'Dupe count {dupe_count}')
        while dupe_count > 0:
            if len(children) >= POPULATION-len(pool.genomes):
                break
            child = breed_child(i)
            child = mutate(child)
            children.append(child)
            dupe_count -= 1

    pool.genomes += children
    np.random.shuffle(pool.genomes)
    pool.generation += 1
    pool.genome_index = 0


def breed_child(genome_index):
    """
    Some of the new genomes should be bred to introduce new parameters that may be more optimal.
    Breeding occurs (currently) with the genome just below itself.
    Breeding uses a normal gaussian dist ratio to interpolate the weights (and biases?) for the new child
    network.
    """
    genom = pool.genomes[genome_index]
    if np.random.random() < BREED_PROBABILITY:
        # Breed
        child = copy.deepcopy(genom)
        # TODO fix at a later time
        #
        # units1 = child.network.units
        # units2 = pool.genomes[genome_index-1].network.units
        #
        # interp_ratio = np.random.normal(0.5, 1)
        #
        # [units1[len(inputs):-len(outputs)] + units1[len(inputs):-len(outputs)]
        # new_len = int(interp_ratio
        # if len(units1) > len(units2):
        #     child.network.units = units1[len(inputs)] + units1[new_len] + units1[-len(outputs)]
        # else:
        #     child.network.units = units2[len(inputs)] + units2[new_len] + units2[-len(outputs)]
    else:
        # Copy
        child = copy.deepcopy(genom)

    return child


def mutate(child):
    """
    We should randomly mutate some of the new genomes to incur new changes to the system.
    Mutation works by potentially adding the number of possible connections/neurons/etc.
    """
    for attr, value in child.__dict__.items():
        if attr == 'fitness' or attr == 'network':
            continue
        if np.random.random() < MUTATE_PROBABILITY:
            setattr(child, attr, value + 1)
    return child


def initialise_run():
    # Init new game
    global fb_game
    fb_game = start_fb_game()
    pool.current_frame = 0

    # Resetting buttons
    fb_game.press_buttons({'Up': False, 'Down': False}, b_network=True)

    if pool.genome_index >= len(pool.genomes):
        new_generation()

    pool.genomes[pool.genome_index].network = generate_network(pool.genomes[pool.genome_index])


def process_run():
    if pool.current_frame % 5 == 0 and pool.current_frame != 0:
        genome = pool.genomes[pool.genome_index]
        button = evaluate_current_genome(genome)
        fb_game.press_buttons(button, b_network=True)


def start_fb_game():
    # We want a single frame update so there can be some input to the network
    fb = flappy_game.FlappyBird()
    fb.frame()
    fb.update_frame()
    return fb


def update_pong_game():
    pool.current_frame += 1
    fb_game.frame()
    fb_game.is_completed = fb_game.player.end_conditions()
    fb_game.update_frame()


if __name__ == '__main__':
    fb_game = None
    pool = initialise_pool()

    while True:
        if not fb_game:
            initialise_run()
            process_run()

        elif fb_game.is_completed:
            genome = pool.genomes[pool.genome_index]

            genome.fitness = np.exp(pool.current_frame / 50)

            if genome.fitness > pool.max_fitness:
                pool.max_fitness = genome.fitness
            pool.genomes[pool.genome_index].fitness = genome.fitness

            pool.genome_index += 1
            print(f'Gen {pool.generation} | Genome first index {pool.genome_index}/{len(pool.genomes)} | complexity {len(pool.genomes[pool.genome_index-1].network.units)} | Fitness {genome.fitness}')

            initialise_run()

        process_run()
        update_pong_game()
