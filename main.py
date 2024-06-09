import datetime
from dataset import WaterfallDataSet

##
# Note: This is a really quick way to get an input from a user. 
# I would normally want to make this a datepicker of some sort with a 
# min date already specified
def get_valid_date(min_date: datetime.date):
    while True:
        user_input = input("Enter a date (MM/DD/YYYY): ")
        try:
            date = datetime.datetime.strptime(user_input, "%m/%d/%Y").date()
            if date < min_date:
                time_str = min_date.strftime("%m/%d/%Y")
                print(f"Invalid date. Date must be > {time_str}")
                continue
            return date
        except ValueError:
            print("Invalid date format. Please try again!")

##
# Note: This is a really quick way to get an input from a user. 
# Ideally, this would be a UI that a user can choose from a list of entity_names 
# and possibly commitement_amounts (if names aren't unique enough)
def get_valid_id(ids: int):
    while True:
        user_input = input("Enter a valid commitement id: ")
        try:
            id = int(user_input)
            if id not in ids:
                print("Invalid id. Id must be in dataset.")
                continue
            return id
        except ValueError:
            print("Invalid id format. Please try again!")

def main(): 
    dataset = WaterfallDataSet()
    dataset.read_commitements('commitments.csv')
    dataset.read_transactions('transactions.csv')
    date = get_valid_date(dataset.min_date)
    id = get_valid_id(dataset.ids)
    dataset.calculate_waterfall(id, date)
    
if __name__ == "__main__":
    main()

