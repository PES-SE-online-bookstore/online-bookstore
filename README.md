# Online Bookstore

Browse books, find your next read, and shop online with the Online Bookstore. You can use the live site right away—no installation needed:

## Visit the bookstore

**[Open the Online Bookstore](https://online-bookstore-10nn.onrender.com)**

Create an account to use customer features such as saving books to your wishlist, adding books to your cart, checking out, and viewing your orders. You can also browse the catalogue and book details without signing in.

## What you can do

- Search the catalogue by book details and narrow results by category or price.
- View book descriptions, availability, and customer reviews.
- Create a buyer account to save books to a wishlist and manage a shopping cart.
- Save shipping addresses and place orders.
- Review your order history and details, cancel eligible orders, or request a return when it is available.
- If you are selling books, register as a seller and submit listings for administrator approval.

> **Please note:** Checkout is currently in test mode. It can create an order with pending payment, but it does not charge your payment method or verify a payment. Please do not treat an order as paid or confirmed based on checkout alone.

## Run the project locally

If you would rather run the project on your own computer, you will need Python 3.11 and PostgreSQL.

### 1. Get the code and install dependencies

```bash
git clone https://github.com/PES-SE-online-bookstore/online-bookstore.git
cd online-bookstore
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Then install the required packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Set up your local database

Create a PostgreSQL database and user, then create a `.env` file in the project folder with your own database credentials:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=online_bookstore
DB_USER=bookstore_user
DB_PASSWORD=replace-with-your-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Replace the sample database values with the database and user you created. Keep `.env` private and do not commit it.

### 3. Prepare and start the site

```bash
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. To administer a local installation, create an administrator account with `python manage.py createsuperuser`, then visit <http://127.0.0.1:8000/admin/>.

## For contributors

Run the project's tests with:

```bash
python manage.py test
```

This project uses Django 5.2, Python 3.11, and PostgreSQL. The production site is hosted on Render; deployment configuration is in `render.yaml`, with build steps in `build.sh`. The health-check endpoint is `/health/`.

## Project documents

- [Software Requirements Specification](docs/online-bookstore_SRS.pdf)
- [Software Architecture Document](docs/Online_Bookstore_SAD.pdf)
- [Online Bookstore Test Plan](docs/Online_Bookstore_Test_Plan.pdf)
- [Deviations from the SRS, SAD and Test Plan](docs/Deviations_from_SRS_SAD_TestPlan.md)
- [Test Plan addendum (test-case table)](docs/Test_Plan_Addendum.md)
- [Test reports: unit, system validation, code and branch coverage](docs/test-reports/)
- [Documents index and status](docs/README.md)
- [High Availability Testing Notes](OBP-30_High_Availability_Testing.txt)
- [Project board](https://pes-1ug24-am311.atlassian.net/jira/software/c/projects/OBP/boards/68/backlog)

## License

No license is currently specified in this repository. Contact the project maintainers before reusing or redistributing the code.
