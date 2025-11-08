from django.db import models

# --- RÈGLE POUR LES RELATIONS ---
# Pour chaque ForeignKey, on_delete est OBLIGATOIRE.
# J'utilise models.CASCADE par défaut pour la plupart des relations, 
# ce qui signifie que si l'objet parent est supprimé, l'enfant l'est aussi.
# Changez-le si vous préférez models.PROTECT ou models.SET_NULL.


class Auteur(models.Model):
    # Laissez Django gérer l'ID automatiquement (Auto-incrémentation)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100, blank=True, null=True)
    nationalite = models.CharField(max_length=50, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    date_deces = models.DateField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True) # Utilisation de auto_now_add
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'auteur'


class Categorie(models.Model):
    # Laissez Django gérer l'ID automatiquement (Auto-incrémentation)
    libelle = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)
    # Relation récursive : utilise 'self'
    parent_categorie = models.ForeignKey(
        'self', models.SET_NULL, blank=True, null=True, related_name='sous_categories'
    ) 

    class Meta:
        db_table = 'categorie'


class Editeur(models.Model):
    libelle = models.CharField(unique=True, max_length=150)
    ville = models.CharField(max_length=100, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'editeur'


class UtilisateurSys(models.Model):
    # Ceci est le modèle pour le personnel de la bibliothèque
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)
    date_derniere_connexion = models.DateTimeField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=100)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'utilisateur_sys'


class Document(models.Model):
    titre = models.CharField(max_length=255)
    annee_publication = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(unique=True, max_length=13, blank=True, null=True)
    resume = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)
    
    # Clés étrangères
    categorie = models.ForeignKey(Categorie, models.PROTECT) # On protège la suppression de la catégorie
    editeur = models.ForeignKey(Editeur, models.PROTECT) # On protège la suppression de l'éditeur
    utilisateur_creation = models.ForeignKey(UtilisateurSys, models.PROTECT) # On protège l'utilisateur créateur

    class Meta:
        db_table = 'document'


class DocumentAuteur(models.Model):
    # Modèle intermédiaire pour la relation N:M entre Document et Auteur
    document = models.ForeignKey(Document, models.CASCADE)
    auteur = models.ForeignKey(Auteur, models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_auteur'
        # Définit la clé composite (Django préfère cela pour les tables N:M)
        unique_together = (('document', 'auteur'),) 


class Emplacement(models.Model):
    code_rayon = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'emplacement'


class TypeMembre(models.Model):
    libelle = models.CharField(unique=True, max_length=50)
    max_emprunt = models.IntegerField()
    duree_emprunt = models.IntegerField()
    taux_penalite_jour = models.DecimalField(max_digits=4, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'type_membre'


class Exemplaire(models.Model):
    numero_inventaire = models.CharField(unique=True, max_length=50)
    etat = models.CharField(max_length=50)
    statut = models.CharField(max_length=50)
    date_mise_en_service = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)
    
    # Clés étrangères
    emplacement = models.ForeignKey(Emplacement, models.PROTECT)
    document = models.ForeignKey(Document, models.CASCADE)
    utilisateur_ajout = models.ForeignKey(UtilisateurSys, models.PROTECT)

    class Meta:
        db_table = 'exemplaire'


class Membre(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_adhesion = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)
    
    # Clé étrangère
    type_membre = models.ForeignKey(TypeMembre, models.PROTECT)

    class Meta:
        db_table = 'membre'


class Emprunt(models.Model):
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour_prevue = models.DateTimeField()
    date_retour_reelle = models.DateTimeField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Clés étrangères
    membre = models.ForeignKey(Membre, models.CASCADE)
    exemplaire = models.ForeignKey(Exemplaire, models.PROTECT)
    utilisateur_emprunt = models.ForeignKey(UtilisateurSys, models.PROTECT)
    # L'utilisateur de retour peut être nul si le document n'est pas encore rentré
    utilisateur_retour = models.ForeignKey(
        UtilisateurSys, 
        models.SET_NULL, 
        related_name='emprunt_utilisateur_retour_set', 
        blank=True, 
        null=True
    )

    class Meta:
        db_table = 'emprunt'


class Penalite(models.Model):
    montant_du = models.DecimalField(max_digits=6, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=6, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    motif = models.CharField(max_length=50)
    statut = models.CharField(max_length=50)
    date_modification = models.DateTimeField(auto_now_add=True)
    
    # Clés étrangères
    membre = models.ForeignKey(Membre, models.CASCADE)
    emprunt = models.ForeignKey(Emprunt, models.SET_NULL, blank=True, null=True)
    utilisateur_creation = models.ForeignKey(UtilisateurSys, models.PROTECT)

    class Meta:
        db_table = 'penalite'


class Permission(models.Model):
    libelle = models.CharField(unique=True, max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'permission'


class Reservation(models.Model):
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_disponibilite = models.DateTimeField(blank=True, null=True)
    statut = models.CharField(max_length=50)
    date_modification = models.DateTimeField(auto_now=True) # Utilisation de auto_now
    date_expiration_mise_de_cote = models.DateTimeField(blank=True, null=True)
    
    # Clés étrangères
    membre = models.ForeignKey(Membre, models.CASCADE)
    document = models.ForeignKey(Document, models.CASCADE)

    class Meta:
        db_table = 'reservation'


class Role(models.Model):
    libelle = models.CharField(unique=True, max_length=50)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'role'


class RolePermission(models.Model):
    # Modèle intermédiaire pour la relation N:M entre Role et Permission
    role = models.ForeignKey(Role, models.CASCADE)
    permission = models.ForeignKey(Permission, models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_permission'
        # Définit la clé composite
        unique_together = (('role', 'permission'),)


class UtilisateurRole(models.Model):
    # Modèle intermédiaire pour la relation N:M entre UtilisateurSys et Role
    utilisateur_sys = models.ForeignKey(UtilisateurSys, models.CASCADE)
    role = models.ForeignKey(Role, models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilisateur_role'
        # Définit la clé composite
        unique_together = (('utilisateur_sys', 'role'),)

