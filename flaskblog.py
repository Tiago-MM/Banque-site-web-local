from flask import Flask, render_template, redirect, url_for, flash, session, request
from forms import RegistrationForm, LoginForm
import pandas as pd
import csv
import email_validator
import os

customers_data = pd.read_csv('customers.csv', delimiter=',')  # Spécifiez le délimiteur utilisé dans le fichier CSV

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'b2363a234a4f3242fe719b04c5636c42'

posts = [
    {
        'author': 'Sherlock Holmes ',
        'title': 'Blog Post 1 ',
        'content': 'First post content ',
        'date_posted': 'September 20, 2023 '
    },
    {
        'author': 'Dr. John Watson ',
        'title': 'Blog Post 2 ',
        'content': 'Second post content ',
        'date_posted': 'September 21, 2023 '
    }
]

def position_dans_alphabet(lettre):
    return ord(lettre.upper()) - ord('A') + 1 if 'A' <= lettre.upper() <= 'Z' else None

EMPLOYEE_USERNAME = 'employee'
EMPLOYEE_PASSWORD = 'A1234'

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About Page')


@app.route("/register", methods=['GET', 'POST'])


def register():
    forms = RegistrationForm()
    if forms.validate_on_submit():
        flash(f'Account created for {forms.username.data}!', 'success')

        # Créer un dictionnaire avec toutes les informations nécessaires
        user_data = {
            'Email': forms.email.data,
            'Password': forms.password.data,
            'Username': forms.username.data,
            'First name': forms.firstname.data,
            'Last name': forms.lastname.data,
            'Balance in savings': 0.0,
            'Balance in current': 0.0
        }

        # Ajouter un nouveau client à la base de données CSV
        add_user_to_csv(
            user_data['Email'],
            user_data['Password'],
            user_data['Username'],
            user_data['First name'],
            user_data['Last name'],
            user_data['Balance in savings'],
            user_data['Balance in current']
        )

        new_firstname = forms.firstname.data
        new_lastname = forms.lastname.data
        new_username = forms.username.data
        profile_picture = request.files['profile_picture']
        point='.'

        filename_picture = f"{new_firstname}{new_lastname}{new_username}{point}{profile_picture.filename[-3:]}"

        # Enregistrer la photo dans le dossier "static"
        if profile_picture and allowed_file(profile_picture.filename):
            profile_picture.save(os.path.join(UPLOAD_FOLDER, filename_picture))

        # Générer le nom de fichier
        filename_prefix = (new_firstname[0]+new_lastname[0]).upper()
        filename_length = len(new_lastname + new_firstname) if len(new_lastname+new_firstname) > 9 else '0'+str(len(new_lastname + new_firstname))
        filename_position_1 = position_dans_alphabet(new_firstname[0]) if len(str(position_dans_alphabet(new_firstname[0]))) > 1 else ('0'+str(position_dans_alphabet(new_firstname[0])))
        filename_position_2 = position_dans_alphabet(new_firstname[1]) if len(str(position_dans_alphabet(new_firstname[1]))) > 1 else ('0'+str(position_dans_alphabet(new_firstname[1])))

        filename = f"{filename_prefix}-{filename_length}-{filename_position_1}-{filename_position_2}.csv"


        
        existing_transactions = []
        try:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                existing_transactions = [row for row in reader]
        except FileNotFoundError:
            pass  # Le fichier n'existe pas encore, c'est normal

        # Sauvegarder la liste mise à jour dans le fichier CSV
        with open(filename, 'w', newline='') as file:
            fieldnames = ["Balance in savings", "Balance in current"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Écrire l'en-tête si le fichier est vide
            if file.tell() == 0:
                writer.writeheader()
                writer.writerow({"Balance in savings": "", "Balance in current": ""})
                #te
                #kz

        return redirect(url_for('customer'))

    return render_template('registration.html', title='Register', form=forms)


def username_exists(username):
    with open('customers.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        return any(row['Username'] == username for row in reader)

def add_user_to_csv(email, password, username, firstname, lastname, balance_savings, balance_current):
    fieldnames = ['Email', 'Password', 'Username', 'First name', 'Last name', 'Balance in savings', 'Balance in current']
    new_user = {
        'Email': email,
        'Password': password,
        'Username': username,
        'First name': firstname,
        'Last name': lastname,
        'Balance in savings': balance_savings,
        'Balance in current': balance_current
    }

    with open('customers.csv', 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')

        # Écrivez une nouvelle ligne pour le nouveau client
        writer.writerow(new_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    log_form = LoginForm()

    email = log_form.email.data
    password = log_form.password.data

    # Rechargez les données depuis le fichier CSV
    customers_data = load_customer_data()

    # Vérifiez si l'email et le mot de passe correspondent aux données du fichier customers.csv
    if check_credentials(email, password, customers_data):
        # Authentification réussie, redirigez vers la page customer
        session['user_email'] = email
        flash('Login successful!', 'success')
        return redirect(url_for('customer'))
    else:
        # Si les informations d'identification sont incorrectes, affichez un message d'erreur
        flash('Login unsuccessful. Please check email and password.', 'danger')
        return render_template('login.html', title='Login', form=log_form)

def load_customer_data():
    # Chargez les données actuelles du fichier CSV
    customers_data = pd.read_csv('customers.csv', delimiter=',')
    return customers_data


def check_credentials(email, password, customers_data):
    # Vérifiez si l'email et le mot de passe correspondent aux données du fichier customers.csv
    matching_customer = customers_data[(customers_data['Email'] == email) & (customers_data['Password'] == password)]

    print(f"Email: {email}, Password: {password}")
    print("Matching customer:")
    print(matching_customer)

    # Renvoie True si des correspondances sont trouvées, sinon False
    return not matching_customer.empty

@app.route("/login1", methods=['GET', 'POST'])
def login1():
    log_form = LoginForm()

    entered_username = log_form.email.data
    entered_password = log_form.password.data

    print(f"Entered Username: {entered_username}")
    print(f"Entered Password: {entered_password}")

    if entered_username == EMPLOYEE_USERNAME and entered_password == EMPLOYEE_PASSWORD:
        # Set cookies or session variables upon successful login
        response = redirect(url_for('employee'))
        response.set_cookie('username', EMPLOYEE_USERNAME)
        response.set_cookie('password', EMPLOYEE_PASSWORD)
        return response
    else:
        print("Login unsuccessful. Please check your username and password.")
        return render_template('login1.html', title='Login', form=log_form)

@app.route("/customer")
def customer():
    # Obtenez l'adresse e-mail de l'utilisateur à partir de la session
    user_email = session.get('user_email')

    if user_email:
        # Obtenez les informations du client actuellement connecté
        current_customer = get_customer_info(user_email)
        try:
            with open('customers.csv', 'r') as file:
                reader = csv.DictReader(file)
                customers = list(reader)
        except FileNotFoundError:
            customers = []
        return render_template('customer.html', customer=current_customer,customers=customers)
    else:
        # Redirigez vers la page de connexion si l'adresse e-mail n'est pas dans la session
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

def get_customer_info(email):
    # Charger les données actuelles du fichier CSV
    with open('customers.csv', 'r') as csvfile:
        fieldnames = ['Email', 'Password', 'Username', 'First name', 'Last name', 'Balance in savings', 'Balance in current']
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',')
        rows = list(reader)

    # Rechercher l'utilisateur par son adresse e-mail (insensible à la casse)
    for row in rows:
        if row['Email'].lower() == email.lower():
            # Retourner les informations du client
            return row

    return None


@app.route("/logout")
def logout():
    # Supprimer l'email de l'utilisateur de la session
    session.pop('user_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



from flask import make_response

# ...

@app.route("/logout1")
def logout1():
    # Supprimer le cookie 'password'
    response = make_response(redirect(url_for('login1')))
    response.delete_cookie('password')
    
    return response

@app.route("/modify_customer", methods=['GET', 'POST'])
def modify_customer():
    if request.method == 'POST':
        # Récupérer les nouvelles informations du formulaire
        new_first_name = request.form.get('new_first_name')
        new_last_name = request.form.get('new_last_name')

        # Obtenez l'adresse e-mail de l'utilisateur à partir de la session
        user_email = session.get('user_email')

        if user_email:
            # Mettre à jour les informations du client dans le fichier CSV
            update_customer_info(user_email, new_first_name, new_last_name)

            flash('Information updated successfully!', 'success')
            return redirect(url_for('customer'))

    return render_template('modify_customer.html', title='Modify Customer')

def update_customer_info(email, new_first_name, new_last_name):
    # Charger les données actuelles du fichier CSV
    with open('customers.csv', 'r') as csvfile:
        fieldnames = ['Email', 'Password', 'Username', 'First name', 'Last name', 'Balance in savings', 'Balance in current']
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter=',')
        rows = list(reader)

    # Rechercher l'utilisateur par son adresse e-mail
    for row in rows:
        if row['Email'] == email:
            # Mettre à jour les informations du client
            row['First name'] = new_first_name
            row['Last name'] = new_last_name

            # Conservez les valeurs actuelles des colonnes de balance
            current_balance_savings = float(row['Balance in savings'])
            current_balance_current = float(row['Balance in current'])

            # Mettez à jour les colonnes de balance avec les valeurs actuelles
            row['Balance in savings'] = current_balance_savings
            row['Balance in current'] = current_balance_current

            # Enregistrez les modifications dans le fichier CSV
            with open('customers.csv', 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
                writer.writerows(rows)

            return
        
@app.route("/add_money", methods=['GET', 'POST'])
def add_money():
    user_email = session.get('user_email')

    if user_email:
        current_customer = customers_data[customers_data['Email'] == user_email].iloc[0]

        if request.method == 'POST':
            amount = request.form.get('amount')

            if amount and amount.isdigit():
                amount = int(amount)

                # Assurez-vous que le solde actuel est un nombre valide
                current_balance = current_customer['Balance in current']
                if pd.notna(current_balance) and str(current_balance).isdigit():
                    current_balance = int(current_balance)
                else:
                    current_balance = 0

                # Ajoutez le montant saisi au solde actuel
                current_customer['Balance in current'] = current_balance + amount

                # Mettez à jour les informations du client dans le fichier CSV
                update_balance(user_email, amount)

                flash('Money added successfully!', 'success')
                return redirect(url_for('customer'))
            else:
                flash('Please enter a valid amount.', 'danger')
                return redirect(url_for('add_money'))

        return render_template('add_money.html', title='Add Money', customer=current_customer)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

def update_balance(email, amount):
    # Chargez les données clients depuis le fichier CSV
    customers_data = pd.read_csv('customers.csv', delimiter=',')

    # Mettez à jour le solde pour l'utilisateur spécifié
    customers_data.loc[customers_data['Email'] == email, 'Balance in current'] += amount

    # Enregistrez les modifications dans le fichier CSV
    customers_data.to_csv('customers.csv', index=False, sep=',')
@app.route("/retray_money", methods=['GET', 'POST'])
def retray_money():
    user_email = session.get('user_email')

    if user_email:
        current_customer = customers_data[customers_data['Email'] == user_email].iloc[0]

        if request.method == 'POST':
            amount = request.form.get('amount')

            if amount and amount.isdigit():
                amount = int(amount)

                # Assurez-vous que le solde actuel est un nombre valide
                current_balance = current_customer['Balance in current']
                if pd.notna(current_balance) and str(current_balance).isdigit():
                    current_balance = int(current_balance)
                else:
                    current_balance = 0.0

                print("Current Balance:", current_balance)
                print("Requested Amount:", amount)

                # Vérifiez si le montant saisi est inférieur ou égal au solde actuel
                if amount <= current_balance:
                    # Soustrayez le montant saisi au solde actuel
                    current_customer['Balance in current'] = current_balance - amount

                    # Mettez à jour les informations du client dans le fichier CSV
                    if update_balance1(user_email, amount):
                        flash('Money subtracted successfully!', 'success')
                    else:
                        flash('Error updating balance. Please try again.', 'danger')

                    return redirect(url_for('customer'))
                else:
                    flash('Not enough money. Please enter a valid amount.', 'danger')
                    return redirect(url_for('retray_money'))
            else:
                flash('Please enter a valid amount.', 'danger')
                return redirect(url_for('retray_money'))

        return render_template('retray_money.html', title='Subtract Money', customer=current_customer)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

def update_balance1(email, amount):
    # Chargez les données clients depuis le fichier CSV
    customers_data = pd.read_csv('customers.csv', delimiter=',')

    # Vérifiez si l'utilisateur existe dans les données
    if email in customers_data['Email'].values:
        # Obtenez l'indice de l'utilisateur dans le DataFrame
        user_index = customers_data[customers_data['Email'] == email].index[0]

        # Obtenez le solde actuel
        current_balance = customers_data.loc[user_index, 'Balance in current']

        # Vérifiez si le retrait ne dépasse pas le solde actuel
        if amount <= current_balance:
            # Soustrayez le montant du solde actuel
            customers_data.loc[user_index, 'Balance in current'] -= amount

            # Enregistrez les modifications dans le fichier CSV
            customers_data.to_csv('customers.csv', index=False, sep=',')

            return True  # Retourne True si la mise à jour a réussi
        else:
            return False  # Retourne False si le solde est insuffisant

    return False  # Retourne False si l'utilisateur n'est pas trouvé dans les données



@app.route("/add_money1", methods=['GET', 'POST'])
def add_money1():
    user_email = session.get('user_email')

    if user_email:
        current_customer = customers_data[customers_data['Email'] == user_email].iloc[0]

        if request.method == 'POST':
            amount = request.form.get('amount')

            if amount and amount.isdigit():
                amount = int(amount)

                # Assurez-vous que le solde actuel est un nombre valide
                current_balance = current_customer['Balance in savings']
                if pd.notna(current_balance) and str(current_balance).isdigit():
                    current_balance = int(current_balance)
                else:
                    current_balance = 0

                # Ajoutez le montant saisi au solde actuel
                current_customer['Balance in savings'] = current_balance + amount

                # Mettez à jour les informations du client dans le fichier CSV
                update_balance2(user_email, amount)

                flash('Money added successfully!', 'success')
                return redirect(url_for('customer'))
            else:
                flash('Please enter a valid amount.', 'danger')
                return redirect(url_for('add_money1'))

        return render_template('add_money1.html', title='Add Money', customer=current_customer)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

def update_balance2(email, amount):
    # Chargez les données clients depuis le fichier CSV
    customers_data = pd.read_csv('customers.csv', delimiter=',')

    # Mettez à jour le solde pour l'utilisateur spécifié
    customers_data.loc[customers_data['Email'] == email, 'Balance in savings'] += amount

    # Enregistrez les modifications dans le fichier CSV
    customers_data.to_csv('customers.csv', index=False, sep=',')

@app.route("/subs_money", methods=['GET', 'POST'])
def subs_money():
    user_email = session.get('user_email')

    if user_email:
        current_customer = customers_data[customers_data['Email'] == user_email].iloc[0]

        if request.method == 'POST':
            amount = request.form.get('amount')

            if amount and amount.isdigit():
                amount = int(amount)

                # Assurez-vous que le solde actuel est un nombre valide
                current_balance = current_customer['Balance in savings']
                if pd.notna(current_balance) and str(current_balance).isdigit():
                    current_balance = int(current_balance)
                else:
                    current_balance = 0

                print("Current Balance (Savings):", current_balance)
                print("Requested Amount:", amount)

                # Vérifiez si le montant saisi est inférieur ou égal au solde actuel
                if amount <= current_balance:
                    # Soustrayez le montant saisi au solde actuel
                    current_customer['Balance in savings'] = current_balance - amount

                    # Mettez à jour les informations du client dans le fichier CSV
                    if update_balance3(user_email, amount):
                        flash('Money subtracted successfully!', 'success')
                    else:
                        flash('Error updating balance. Please try again.', 'danger')

                    return redirect(url_for('customer'))
                else:
                    flash('Not enough money. Please enter a valid amount.', 'danger')
                    return redirect(url_for('subs_money'))
            else:
                flash('Please enter a valid amount.', 'danger')
                return redirect(url_for('subs_money'))

        return render_template('subs_money.html', title='Subtract Money', customer=current_customer)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))


def update_balance3(email, amount):
    # Chargez les données clients depuis le fichier CSV
    customers_data = pd.read_csv('customers.csv', delimiter=',')

    # Vérifiez si l'utilisateur existe dans les données
    if email in customers_data['Email'].values:
        # Obtenez l'indice de l'utilisateur dans le DataFrame
        user_index = customers_data[customers_data['Email'] == email].index[0]

        # Obtenez le solde actuel
        current_balance = customers_data.loc[user_index, 'Balance in savings']

        # Vérifiez si le retrait ne dépasse pas le solde actuel
        if amount <= current_balance:
            # Soustrayez le montant du solde actuel
            customers_data.loc[user_index, 'Balance in savings'] -= amount

            # Enregistrez les modifications dans le fichier CSV
            customers_data.to_csv('customers.csv', index=False, sep=',')

            return True  # Retourne True si la mise à jour a réussi
        else:
            return False  # Retourne False si le solde est insuffisant

    return False  # Retourne False si l'utilisateur n'est pas trouvé dans les données







#employee part 
@app.route("/employee", methods=['GET', 'POST'])
def employee():
    if not is_authenticated():
        # If not authenticated, redirect to the login page
        return redirect(url_for('login1'))
    

    try:
        with open('customers.csv', 'r') as file:
            reader = csv.DictReader(file)
            customers = list(reader)
    except FileNotFoundError:
        customers = []

    return render_template('employee.html', title='Employee Page', customers=customers)

def is_authenticated():
    return request.cookies.get('username') == EMPLOYEE_USERNAME and \
           request.cookies.get('password') == EMPLOYEE_PASSWORD


customers = []
with open('customers.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Ignore the header row
        for row in reader:
            customer = {'First name': row[3], 'Last name': row[4],'Balance in savings': row[5],'Balance in current': row[6]}
            customers.append(customer)


UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'jpg'}  

@app.route("/add_customer", methods=['POST'])
def add_customer():



    new_firstname = request.form.get('new_firstname')
    new_lastname = request.form.get('new_lastname')
    new_email = request.form.get('new_email')
    new_password = request.form.get('new_password')
    new_username=request.form.get('new_username')


    # Ajoutez le nouveau client à votre liste de clients
    new_customer = {'First name': new_firstname, 'Last name': new_lastname,'Username':new_username, 'Email':new_email, 'Password':new_password, 'Balance in savings':0.0,'Balance in current': 0.0}
    customers.append(new_customer)

        # Générer le nom de fichier
    filename_prefix = (new_firstname[0]+new_lastname[0]).upper()
    filename_length = len(new_lastname + new_firstname) if len(new_lastname+new_firstname) > 9 else '0'+str(len(new_lastname + new_firstname))
    filename_position_1 = position_dans_alphabet(new_firstname[0]) if len(str(position_dans_alphabet(new_firstname[0]))) > 1 else ('0'+str(position_dans_alphabet(new_firstname[0])))
    filename_position_2 = position_dans_alphabet(new_firstname[1]) if len(str(position_dans_alphabet(new_firstname[1]))) > 1 else ('0'+str(position_dans_alphabet(new_firstname[1])))

    filename = f"{filename_prefix}-{filename_length}-{filename_position_1}-{filename_position_2}.csv"


    
    existing_transactions = []
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            existing_transactions = [row for row in reader]
    except FileNotFoundError:
        pass  # Le fichier n'existe pas encore, c'est normal

    # Sauvegarder la liste mise à jour dans le fichier CSV
    with open(filename, 'w', newline='') as file:
        fieldnames = ["Balance in savings", "Balance in current"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Écrire l'en-tête si le fichier est vide
        if file.tell() == 0:
            writer.writeheader()
            writer.writerow({"Balance in savings": "", "Balance in current": ""})
            #te
            #kz

        





    #fichier customers

    existing_customers = []
    try:
        with open('customers.csv', 'r') as file:
            reader = csv.DictReader(file)
            existing_customers = [row for row in reader]
    except FileNotFoundError:
        pass  # Le fichier n'existe pas encore, c'est normal

    # Ajouter le nouveau client à la liste existante
    existing_customers.append(new_customer)

    # Sauvegarder la liste mise à jour dans le fichier CSV
    with open('customers.csv', 'w', newline='') as file:
        fieldnames = ["Email","Password","Username","First name","Last name","Balance in savings","Balance in current"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Écrire l'en-tête si le fichier est vide
        if file.tell() == 0:
            writer.writeheader()

        # Écrire les données des clients
        writer.writerows(existing_customers)

    # Redirigez l'utilisateur vers la page de l'employé

    filename_picture = f"{new_firstname}{new_lastname}{new_username}.jpg"

    # Enregistrer la photo dans le dossier "static"
    profile_picture = request.files['profile_picture']
    if profile_picture and allowed_file(profile_picture.filename):
        profile_picture.save(os.path.join(UPLOAD_FOLDER, filename_picture))


    return redirect(url_for('employee'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/delete_customer/<int:customer_id>", methods=['GET'])
def delete_customer(customer_id):
    #customer_id
    if not customers:
        flash("Aucun client à supprimer.")
        return redirect(url_for('employee'))

    if 1 <= customer_id <= len(customers):
        # Supprimer le client de la liste en mémoire
        deleted_customer = customers.pop(customer_id - 1)

        # Lire le contenu existant du fichier CSV
        existing_customers = []
        try:
            with open('customers.csv', 'r') as file:
                reader = csv.DictReader(file)
                existing_customers = [row for row in reader]
        except FileNotFoundError:
            pass  # Le fichier n'existe pas encore, c'est normal

        # Supprimer le client spécifique de la liste existante
        existing_customers.pop(customer_id - 1)

        # Afficher des informations de débogage
        print("Clients actuels en mémoire:", customers)
        print("Clients actuels dans le fichier CSV:", existing_customers)

        # Écrire l'ensemble dans le fichier CSV
        with open('customers.csv', 'w', newline='') as file:
            fieldnames = ["Email","Password","Username","First name","Last name","Balance in savings","Balance in current"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Écrire l'en-tête si le fichier est vide
            if file.tell() == 0:
                writer.writeheader()

            # Écrire les données des clients
            writer.writerows(existing_customers)

        flash(f"Le client {deleted_customer['First name']} {deleted_customer['Last name']} a été supprimé avec succès.")
    else:
        flash("Index de client invalide.")

    return redirect(url_for('employee'))





      

@app.route("/Aboutcustomer/<int:customer_id>/<string:link>", methods=['GET'])
def About(customer_id,link):
    if (link=="employee" and (not is_authenticated())):
        # If not authenticated, redirect to the login page
        return redirect(url_for('login1'))
    
    customer_info = load_customer_info(customer_id)
    if customer_info:
        first_line, other_lines = get_file_info(customer_info)
        saving,current=getmoneycustomer(customer_id)
        return render_template('Aboutcustomer.html', title='About Customer',first_line=first_line, other_lines=other_lines,customer_info=customer_info,saving=saving,current=current,customer_id=customer_id,link=link)
    else:
        return render_template('Aboutcustomer.html', title='About Customer',customer_info=customer_info,customer_id=customer_id,link=link)

def load_customer_info(customer_id):
    # Charger les informations du client depuis le fichier customers.csv
    with open('customers.csv', 'r') as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            if index == customer_id:
                # Récupérer les informations nécessaires
                first_name = row['First name']
                last_name = row['Last name']

                # Générer le nom de fichier
                filename_prefix = (first_name[0] + last_name[0]).upper()
                filename_length = len(first_name + last_name) if len(first_name + last_name) > 9 else '0' + str(len(first_name + last_name))
                filename_position_1 = position_dans_alphabet(first_name[0]) if len(str(position_dans_alphabet(first_name[0]))) > 1 else ('0' + str(position_dans_alphabet(first_name[0])))
                filename_position_2 = position_dans_alphabet(first_name[1]) if len(str(position_dans_alphabet(first_name[1]))) > 1 else ('0' + str(position_dans_alphabet(first_name[1])))

                filename = f"{filename_prefix}-{filename_length}-{filename_position_1}-{filename_position_2}.csv"
                return filename
            
    # Si le client n'est pas trouvé dans customers.csv
    return None


def getmoneycustomer(customer_id):
    # Charger les informations du client depuis le fichier customers.csv
    with open('customers.csv', 'r') as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            if index == customer_id:
                # Récupérer les informations nécessaires
                saving = row['Balance in savings']
                current = row['Balance in current']
        
        return saving,current
            
    # Si le client n'est pas trouvé dans customers.csv
    return None






def get_file_info(file_path):
    first_line = None
    other_lines = []

    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)

            # Lire la première ligne
            first_line = next(reader, None)

            # Lire les autres lignes
            for row in reader:
                other_lines.append(row)
    except FileNotFoundError:
        pass  # Gérer le cas où le fichier n'est pas trouvé

    return first_line, other_lines


@app.route("/update_balances/<int:customer_id>/<account_type>/<customer_info>/<link>", methods=['POST'])
def update_balances(customer_id, account_type,customer_info,link):

    data=[]
    amount = float(request.form['amount'])
    operationaddorwithdraw = request.form['operation']
    operation = request.form['nameoperation']

    if(operationaddorwithdraw=="withdraw"):amount*=(-1)
    # Update data with new entry
    if(account_type=="savings"):
        new_entry = {'operation': operation, 'amount': amount}
        fieldnames = ['operation', 'amount']
    else:
        new_entry = {'a':"",'b':"",'operation': operation, 'amount': amount}
        fieldnames = ['a','b','operation', 'amount']

    data.append(new_entry)


    #Neg value
    value=0
    with open('customers.csv', 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        for index, row in enumerate(rows):
            if index == (customer_id-1):
                    total=float(row['Balance in '+account_type]) + amount


    if(operationaddorwithdraw=="withdraw"):amount*=(-1)
    if(total>=0 and amount >=0):
        if(operationaddorwithdraw=="withdraw"):amount*=(-1)
        try:
            with open(customer_info, 'r') as file:
                reader = csv.DictReader(file)
                data = list(reader)  # Read existing data into a list of dictionaries
        except FileNotFoundError:
            data = []  # File doesn't exist yet, initialize data as an empty list



        # Write data back to the CSV file
        with open(customer_info, 'a', newline='') as file:  # Use 'a' (append) mode instead of 'w'
            writer = csv.writer(file)
            
            # Write an empty row if the file is not empty
            if file.tell() == 0:
                writer.writerow(fieldnames)

            # Write the data on a new line without an extra comma at the beginning
            writer.writerows("")
            writer.writerow([new_entry[field] for field in fieldnames])



            fieldnames=["Email","Password","Username","First name","Last name","Balance in savings","Balance in current"]

            # Update balance in the 'customers.csv' file
            with open('customers.csv', 'r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            for index, row in enumerate(rows):
                if index == (customer_id-1):
                    if account_type == "savings":
                        row['Balance in savings'] = str(float(row['Balance in savings']) + amount)
                    else:
                        row['Balance in current'] = str(float(row['Balance in current']) + amount)

            # Write the updated data back to 'customers.csv'
            with open('customers.csv', 'w', newline='') as file:
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    else:
        total

    return redirect(url_for('About', customer_id=customer_id,link=link))

if __name__ == '__main__':
    app.run(debug=True)
