import re

test_cases = [
    'PiS(188) GŁOSOWAŁO',
    'KO(220) GŁOSOWAŁO',
    'PSL-TD(63) GŁOSOWAŁO',
    'Konfederacja_KP(3) GŁOSOWAŁO',
    'niez.(4) GŁOSOWAŁO'
]

pattern = r'^([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż_.]+)\([0-9]+\)'

for line in test_cases:
    match = re.search(pattern, line)
    if match:
        print(f'✓ {line:30s} -> {match.group(1)}')
    else:
        print(f'✗ {line:30s} -> NO MATCH')

# Test z myślnikiem
print('\n--- Test z myślnikiem ---')
pattern_with_dash = r'^([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż_.-]+)\([0-9]+\)'

for line in test_cases:
    match = re.search(pattern_with_dash, line)
    if match:
        print(f'✓ {line:30s} -> {match.group(1)}')
    else:
        print(f'✗ {line:30s} -> NO MATCH')

