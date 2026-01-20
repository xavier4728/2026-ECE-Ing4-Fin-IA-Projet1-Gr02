# groupe-JVX/src/strategy_genes.py
import random
from .config import Config

def get_gene_ranges():
    """Récupère les plages de paramètres depuis Config."""
    return Config.GENE_BOUNDS

def generate_individual():
    """Génère un individu (Compatible Tuples ET Dictionnaires)."""
    ranges = get_gene_ranges()
    individual = {}
    
    for gene, params in ranges.items():
        # === CAS 1 : CONFIG TUPLE (Votre mode Turbo) ===
        if isinstance(params, tuple):
            min_val, max_val = params
            # Si l'un des nombres est un float (ex: 0.05), on génère un float
            if isinstance(min_val, float) or isinstance(max_val, float):
                individual[gene] = round(random.uniform(min_val, max_val), 5)
            else:
                # Sinon on génère un entier
                individual[gene] = random.randint(min_val, max_val)
        
        # === CAS 2 : CONFIG DICTIONNAIRE (Legacy) ===
        elif isinstance(params, dict):
            if isinstance(params['min'], int):
                individual[gene] = random.randrange(params['min'], params['max'] + 1, params['step'])
            else:
                steps = int((params['max'] - params['min']) / params['step'])
                val = params['min'] + (random.randint(0, steps) * params['step'])
                individual[gene] = round(val, 5)
            
    return individual

def mutate_individual(individual, indpb):
    """Mutation robuste (Compatible Tuples ET Dictionnaires)."""
    ranges = get_gene_ranges()
    for gene in individual:
        if random.random() < indpb:
            params = ranges[gene]
            
            # === CAS 1 : CONFIG TUPLE ===
            if isinstance(params, tuple):
                min_val, max_val = params
                if isinstance(min_val, float) or isinstance(max_val, float):
                    individual[gene] = round(random.uniform(min_val, max_val), 5)
                else:
                    individual[gene] = random.randint(min_val, max_val)
            
            # === CAS 2 : CONFIG DICTIONNAIRE ===
            elif isinstance(params, dict):
                if isinstance(params['min'], int):
                    individual[gene] = random.randrange(params['min'], params['max'] + 1, params['step'])
                else:
                    steps = int((params['max'] - params['min']) / params['step'])
                    val = params['min'] + (random.randint(0, steps) * params['step'])
                    individual[gene] = round(val, 5)
                    
    return individual,

def decode_chromosome(individual):
    """Retourne l'individu tel quel (format dictionnaire)."""
    return individual