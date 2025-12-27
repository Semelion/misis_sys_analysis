def show_graph(content):
    pairs = [item.split(',') for item in content.split('\n')]

    apexes = set([item[0] for item in pairs])#.add([item[1] for item in pairs])
    apexes.update([item[1] for item in pairs])
    apexes = sorted(apexes)

    n = len(apexes)

    matrix = [[0]*n for i in range(n)]
    
    for pair in pairs:
        f_idx = apexes.index(pair[0])
        s_idx = apexes.index(pair[1])

        matrix[f_idx][s_idx] = 1

    return matrix

print(show_graph("1,2\n1,3\n3,4\n3,5"))
