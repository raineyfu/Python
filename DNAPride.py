length = input()
for x in range(int(length)):
    strLength = input()
    strInput = input()
    output = ''
    for elem in strInput:
        if (elem == 'A'):
            output += 'T'
        if (elem == 'T'):
            output += 'A'
        if (elem == 'G'):
            output += 'C'
        if (elem == 'C'):
            output += 'G'
        if (elem == 'U'):
            output = "Error RNA nucleobases found!"
            break

    print(output)

