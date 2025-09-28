import random 

soma = 21
print ("Jogo dos fósforos. O jogo começa com 21 fósforos e cada jogador pode tirar entre 1 a 4 fósforos. Quem tirar o último perde")

play = int (input ("Quem começa a jogar? (1= jogador, 2= computador) "))

if play == 1:

    while soma > 1:
        n = int (input("Diz um número de fósforos (1-4): "))
        while n < 1 or n > 4 or n > soma:
            print ("Número inválido, tens que escolher de 1 a 4, e de acordo com os fósforos que ainda estão na caixa. ")
            n = int(input("Diz um número de fósforos que queres tirar (1-4) "))

        
        soma -= n
        print(f"Tiraste {n} fósforos. Faltam {soma} fósforos. ")

        if soma == 1:
            print ("Tu ganhaste, o computador perdeu o jogo.")
            break

        comp = min(5 - n, soma -1)
        soma -= comp
        print(f"O computador tirou {comp} fósforos. Faltam {soma} fósforos.")

        if soma == 1:
            print("Tu perdeste, o computador ganhou!")
            break

else: 

    comp = random.randint(1,4)
    soma -= comp
    print(f"O computador tirou {comp} fósforos. Faltam {soma} fósforos.")

    while soma > 1:
        n = int(input("Diz um número de fósforos que queres tirar (1-4): "))
        while n < 1 or n > 4 or n > soma:
            print("Número inválido, escolhe um número entre 1 e 4, e não maior que os fósforos que estão na caixa.")
            n = int(input("Diz um número de fósforos (1-4): "))

        soma -= n
        print (f"Tiraste {n} fósforos. Faltam {soma} fósforos. ")

        if soma == 1:
            print ("Tu ganhaste, o computador perdeu! ")
            break

        if soma % 5 != 1:
            comp = (soma - 1) % 5
            if comp == 0:
                comp = random.randint (1, min(4, soma -1))
        else:
            comp = random.randint(1, min(4, soma - 1))

        soma -= comp
        print(f"O computador tirou {comp} fósforos. Faltam {soma} fósforos.")

        if soma == 1:
            print("Tu perdeste, o computador ganhou!")
            break
