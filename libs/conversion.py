from math import cos,sin,pi,sqrt

## Objectif : Convertir les coordonnées du plateau, des tages ArUco et des caméras d'une base centrée sur la caméra et une base centrée sur l'origine du plateau.

## Tous les angles utilisés sont dans le sens trigonométrique.

#Dictionnaire des tags ArUCO avec leurs positions.
dict_aruco = {
    #Les 4 tags au sol.
    "id20" : (0550.0, 1350.0, 0.0),
    "id21" : (2350.0, 1350.0, 0.0),
    "id22" : (0550.0, 0550.0, 0.0),
    "id23" : (2350.0, 0550.0, 0.0),
}


def conversion(x : float,y : float,z : float, tx : float, ty : float, tz : float, closest_tag : str) -> (float,float,float) : #Update : L'idée de passer par 3 rotations successives est un échec. Va falloir faire une V3 avec les quaternions.
    '''
    2e essai avec juste les paramètres de la caméra. Et les valeurs mesurées d'un tag ArUCO.
    :param x: Coordinates x of ArUCO tag
    :param y: Coordinates y of ArUCO tag
    :param z: Coordinates z of ArUCO tag
    :param tx: Angle tx of camera
    :param ty: Angle ty of camera
    :param tz: Angle tz of camera
    :param: closest_tag : str Closest ArUCO tag from the camera
    :return: Position of camera based on the board
    '''

    #Vérification que les valeurs sont cohérentes.
    assert(z>=0), "La position mesurée par la caméra n'est pas cohérente."

    #Position of ArUCO tag based on the new coordinate system
    new_coordinates = rotation_3D(x,y,z,"x", tx)
    print(new_coordinates)
    new_coordinates = rotation_3D(new_coordinates[0], new_coordinates[1], new_coordinates[2],"y", ty)
    print(new_coordinates)
    new_coordinates = rotation_3D(new_coordinates[0], new_coordinates[1], new_coordinates[2],"z", tz)
    print(new_coordinates)

    #Translation vers le plateau
    final_coordinates = translation_3D(new_coordinates[0],new_coordinates[1],new_coordinates[2],dict_aruco[closest_tag])
    print(new_coordinates)
    #Les coordonnées enfin dans le bon repère
    #height = y*cos(deg_to_rad(tx))
    coordinates = (final_coordinates[0], final_coordinates[1],final_coordinates[2])

    #Vérification que les coordonnées sont bien dans l'aire de jeu.
    #assert(x>=-30 and x<=3030 and y>=-30 and y<=2030), "Le tag est situé en dehors du plateau de jeu." #3 cm de marge pour l'instant comme c'est ce qu'on a en merge d'erruer actuellement.

    return coordinates

def deg_to_rad(theta : float) :
    '''
    Convertit un angle du degré au radian.
    :param theta: L'angle en question.
    :return:
    '''
    return theta * pi/180


def rotation_3D(x : float,y : float,z : float,axis : str,theta : float) :
    '''
    Réalise une rotation 'theta' selon l'axe 'axis' dans un même repère à 3 dimensions.
    :param x: Coordonnées du point selon l'axe x
    :param y: Coordonnées du point selon l'axe y
    :param z: Coordonnées du point selon l'axe z
    :param axis: L'axe (x,y ou z) de rotation.
    :param theta: L'angle de rotation
    :return:
    '''
    theta = deg_to_rad(theta) #Les fonctions trigonométriques demandent un angle en radian.
    assert (axis == "x" or axis == "y" or axis == "z"), "Les axes ne peuvent être que x, y ou z."
    if axis == "x" :
        return x, cos(theta) * y + sin(theta) * z, - sin(theta) * y + cos(theta) * z
    if axis == "y" :
        return cos(theta) * x - sin(theta) * z,y, sin(theta) * x + cos(theta) * z
    return cos(theta) * x + sin(theta) * y, - sin(theta) * x + cos(theta) * y,z

def translation_3D(x : float, y : float, z : float,n : (float, float, float))->(float, float, float) :
    '''
    Réalise une translation d'un point de coordonnées (x,y,z) d'une valeur n = [xt,yt,zt]
    :param x: Coordonnées du point selon l'axe x
    :param y: Coordonnées du point selon l'axe y
    :param z: Coordonnées du point selon l'axe z
    :param n: Translation de coordonnées (xt,yt,zt)
    :return:
    '''
    return -x + n[0], -y + n[1], -z + n[2]  # Par convention. (on va de la caméra vers l'aire de jeu)

def main() :
    #Fonction principale

    #Tests
    test_rotation3D()
    print("\n")
    test_conversion()
    print("Hello World !")

##Jeux de tests

def test_rotation3D() :
    '''
    :return: Jeu de test sur rotation3D(). Renvoie une erreur en cas d'échec.
    '''
    test_1 = rotation_3D(0,0,0, "x",0)
    test_2 = rotation_3D(100,50,150, "x",39)
    test_3 = rotation_3D(100,50,150, "y",39)
    test_4 = rotation_3D(100,50,150, "z",39)
    test_5 = rotation_3D(1,2,3, "x",90)
    #test_6 = rotation_3D(0,0,0, "f",0) # Renvoie une AssertionError.
    print(f"Test 1 : {test_1}\nShould return : (0,0,0)")
    print(f"Test 2 : {test_2}\nShould return : (100,-55.54,148.04)")
    print(f"Test 3 : {test_3}\nShould return : (172.11,50,53.64)")
    print(f"Test 4 : {test_4}\nShould return : (46.25,101.79,150)")
    print(f"Test 5 : {test_5}\nShould return : (1,-3,2)")

def test_conversion() :
    '''
    :return: Jeu de test sur conversion().
    '''

    #La caméra est située 10 cm au-dessus du tag 20.
    test_1 = conversion(0,0,100,0, -180, 180, "id22")
    error_xyz_1 = (test_1[0]-550,test_1[1]-550,test_1[2]-100)
    dist_error_1 = sqrt(error_xyz_1[0]**2+error_xyz_1[1]**2+error_xyz_1[2]**2)
    print(f"Test 1 : {test_1}\nShould return : (550,550,100).\nErreur sur chaque coordonnée : {error_xyz_1}.\nDistance d'erreur : {dist_error_1} mm.\n\n")

    #Position de la caméra 1 par rapport au tag 23 (Valeurs mesurées approximatives)
    test_2 = conversion(-50,380,1050,111,20,-35,"id23")
    error_xyz_2 = (test_2[0]-3000,test_2[1]-0,test_2[2]-1000)
    dist_error_2 = sqrt(error_xyz_2[0]**2+error_xyz_2[1]**2+error_xyz_2[2]**2)
    print(f"Test 2 : {test_2}\nShould return : (3000,0,1000).\nErreur sur chaque coordonnée : {error_xyz_2}.\nDistance d'erreur : {dist_error_2} mm.\n\n")

    #Position de la caméra 2 par rapport au tag 21 (Valeurs théoriques)
    test_3 = conversion(0,0,1358.3077707206126,-135,0,45,"id21")
    error_xyz_3 = (test_3[0]-3000,test_3[1]-2000,test_3[2]-1000)
    dist_error_3 = sqrt(error_xyz_3[0]**2+error_xyz_3[1]**2+error_xyz_3[2]**2)
    print(f"Test 3 : {test_3}\nShould return : (3000,2000,1000).\nErreur sur  chaque coordonnée : {error_xyz_3}.\nDistance d'erreur : {dist_error_3} mm.\n\n")

## Exécution du main

if __name__ == "__main__":
    main()
