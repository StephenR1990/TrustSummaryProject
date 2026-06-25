# some basic automated testing
import unittest
from main import check_int
import main as flask_app
import tempfile

from werkzeug.security import generate_password_hash


class TestPlan(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()

        flask_app.app.config.update({
            "TESTING": True,
            "DATABASE": self.db_path,
            "SECRET_KEY": "test-secret-key"
        })
        self.app = flask_app.app
        self.client = self.app.test_client()
        # create a test db to not affect data.db
        with self.app.app_context():
            db = flask_app.get_db()
            db.executescript("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    fullname TEXT NOT NULL,
                    accounttype TEXT NOT NULL
                );

                CREATE TABLE DailySummary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dte TEXT,
                    SiteManager TEXT,
                    PatientsInCorridor INTEGER,
                    EscalationLevel TEXT,
                    TriageTimehrs TEXT,
                    PatientsAwaitingBeds INTEGER,
                    WaitingTimeMajorshrs TEXT,
                    TotalPatientsED INTEGER
                );
            """)

            db.execute(
                "INSERT INTO users(username, password, fullname, accounttype) VALUES (?, ?, ?, ?)",
                ("SRogers", generate_password_hash("Test1234"), "SteveRogers", "Admin")
            )

            db.execute("""
                INSERT INTO DailySummary
                (dte, SiteManager, PatientsInCorridor, EscalationLevel,
                 TriageTimehrs, PatientsAwaitingBeds, WaitingTimeMajorshrs, TotalPatientsED)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("01-01-2026", "Smith", 5, "Green", "1", 2, "3", 40))

            db.commit()

    # test the integer check function
    def test_check_int_valid(self):
        self.assertEqual(check_int("5"), 5)

    def test_check_int_invalid(self):
        self.assertEqual(check_int("abc"), 0)

    def test_check_int_negative(self):
        self.assertEqual(check_int("-1"), -1)

    def test_check_int_decimal(self):
        self.assertEqual(check_int("5.2"), 0)

    # test login
    def test_login(self):
        return self.client.post("/", data={
            "username": "SRogers",
            "password": "Test1234"
        }, follow_redirects=True)

    # test if user enter invalid login detials
    def test_login_invalid_user_shows_error(self):
        response = self.client.post("/", data={
            "username": "wrong",
            "password": "wrong"
        })
        self.assertIn(b"Incorrect username/password!", response.data)

    # test if a user tries to access the summary list without being logged in
    def test_summary_requires_login(self):
        response = self.client.get("/summarylist")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.location)

    # test trying to insert a record with a invlaid date
    def test_add_daily_record_invalid_date(self):
        self.test_login()

        response = self.client.post("/adddailyrecord", data={
            "ReportDate": "bad-date",
            "SiteManager": "Smith",
            "PatientsInCorridor": "5",
            "EscalationLevel": "Green",
            "TriageTimehrs": "1",
            "PatientsAwaitingBeds": "2",
            "WaitingTimeMajorshrs": "3",
            "TotalPatientsED": "50"
        })

        self.assertIn(b"Please enter a valid date", response.data)
