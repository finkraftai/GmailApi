from label import main as create_label
from filter import main as apply_filter
from EmailCount import main as count_emails_per_day
from Details_each_mail import main as save_email_details

if __name__ == "__main__":
    create_label()
    apply_filter()
    count_emails_per_day()
    save_email_details()