import mysql.connector
import datetime


connect = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='1223334444',
    database='databasesproject'
)

def getRoleID(role, connect):
    db = connect.cursor()
    db.execute(fr"SELECT RoleID FROM duties WHERE Description = %s", (role,))
    ID = db.fetchone()[0]
    return ID

def getName(employeeID, connect):
    db = connect.cursor()
    db.execute(fr"SELECT name FROM employee WHERE EmployeeID = %s", (employeeID,))
    ID = db.fetchone()[0]
    return ID

def login(name, connect):
    db = connect.cursor()
    db.execute(fr"SELECT EmployeeID FROM employee WHERE name = %s", (name,))
    ID = db.fetchone()[0]
    return ID


def changeRole(name, roleID, connect):
    db = connect.cursor()
    db.execute("UPDATE employee SET RoleID = %s WHERE name = %s", (roleID, name))
    connect.commit()


def getItem(itemName, connect):
    db = connect.cursor()
    db.execute(fr"SELECT itemID FROM itemStock WHERE itemName = %s", (itemName,))
    ID = db.fetchone()[0]
    return ID


def newTransaction(isExport, companyName, employeeID, connect):
    db = connect.cursor()
    db.execute("SELECT MAX(TransactionID) FROM transaction")
    transID = db.fetchone()[0] + 1
    db.execute("INSERT INTO transaction (TransactionID, CompanyName, Delivery, Arrival, isExport, EmployeeID) "
               "VALUES (%s, %s, %s, %s, %s, %s);",
               (transID, companyName, str(datetime.datetime.now()), str(datetime.datetime.now() + datetime.timedelta(days=7)), isExport, employeeID))
    connect.commit()
    return transID


def newSales(transaction, itemID, amount, price, connect):
    db = connect.cursor()
    db.execute("SELECT SaleID FROM sales WHERE TransactionID = %s AND ItemID = %s AND price = %s", (transaction, itemID, price))
    result = db.fetchall()
    if len(result) == 0:
        db.execute("SELECT MAX(SaleID) FROM sales")
        saleID = db.fetchone()[0] + 1
        db.execute("INSERT INTO sales (SaleID, TransactionID, ItemID, Amount, price) "
                   "VALUES (%s, %s, %s, %s, %s);",
                   (saleID, transaction, itemID, amount, price))
    else:
        db.execute("SELECT Amount FROM sales WHERE SaleID = %s", result[0])
        amt = db.fetchone()[0]
        db.execute("UPDATE sales SET Amount = %s WHERE SaleID = %s", (amt + amount, result[0][0]))
    db.execute("SELECT isExport FROM transaction WHERE transactionID = %s", (transaction,))
    isExport = db.fetchone()[0]
    db.execute("SELECT stockAmount FROM itemstock WHERE itemID = %s", (itemID,))
    stockamount = db.fetchone()[0]
    db.execute("UPDATE itemstock SET stockAmount = %s WHERE itemID = %s", ((stockamount - amount) if isExport else (stockamount + amount), itemID))
    connect.commit()

def getBill(transID, connect):
    db = connect.cursor()
    db.execute("SELECT itemstock.itemName, sales.amount, sales.price FROM sales "
               "JOIN itemstock ON sales.itemID = itemstock.itemID "
               "WHERE sales.transactionID = %s;", (transID,))
    result = db.fetchall()
    total = 0
    for r in result:
        total += r[1] * r[2]
        print(f"{r[0]} {r[1]}pcs @Rp{r[2]} each, total Rp{r[1] * r[2]}")
    print("Total: Rp", total)


def processBill(transID, connect):
    db = connect.cursor()
    db.execute("SELECT isExport FROM transaction WHERE transactionID = %s", (transID,))
    isExport = db.fetchone()[0]
    while True:
        itemID = getItem(input(f"Enter item name to {'import' if not isExport else 'export'}: "), connect)
        amt = int(input(f"Enter amount of items to {'import' if not isExport else 'export'}: "))
        price = int(input(f"Enter price to {'import' if not isExport else 'export'} at: "))
        newSales(transID, itemID, amt, price, connect)
        if input("Close bill? [Y/N]: ") == 'Y':
            getBill(transID, connect)
            break


employee = login(input("Enter your name: "), connect)

print("Welcome,", getName(employee, connect))
print("1. Change Role")
print("2. Open new bill")
select = input("Enter selection: ")

if select == '2':
    isExport = True if input("Import or Export? [I/E]:") == 'E' else False
    company = input(f"Enter company name to {'import from'if not isExport else 'export to'}: ")
    processBill(newTransaction(isExport, company, employee, connect), connect)

else:
    changeRole(getName(employee, connect), getRoleID(input("Enter role name: "), connect), connect)
