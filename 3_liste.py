bicikla=['tocak', 'lanac', 'sasija', 'pedala' ]
print(bicikla)

print(bicikla[3].title())
print(bicikla[2].title())

message = f"Skorije sam zamenio {bicikla[2]}"
print(message)

bicikla.insert(0, 'kaciga')
print(bicikla)

del bicikla[1]
print(bicikla)