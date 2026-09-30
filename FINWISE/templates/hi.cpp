#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
using namespace std;

// Define Employee structure to store the employee details
struct Employee {
    int empID;
    string name;
    string designation;
    double salary;

    // Constructor for easy creation of an Employee object
    Employee(int id = 0, string n = "", string d = "", double s = 0.0)
        : empID(id), name(n), designation(d), salary(s) {}
};

// Function to write the employee data into the file
void writeEmployeeData(const string& filename, const Employee& emp) {
    fstream file;
    file.open(filename, ios::out | ios::app | ios::binary);
    if (!file) {
        cerr << "Error in opening file!" << endl;
        return;
    }
    file.write(reinterpret_cast<const char*>(&emp), sizeof(emp));
    file.close();
}

// Function to display employee details
void displayEmployee(const Employee& emp) {
    cout << "Employee ID: " << emp.empID << endl;
    cout << "Name: " << emp.name << endl;
    cout << "Designation: " << emp.designation << endl;
    cout << "Salary: " << emp.salary << endl;
}

// Function to search for an employee by ID
bool searchEmployeeByID(const string& filename, int empID, Employee& emp) {
    fstream file;
    file.open(filename, ios::in | ios::binary);
    if (!file) {
        cerr << "Error in opening file!" << endl;
        return false;
    }
    bool found = false;
    while (file.read(reinterpret_cast<char*>(&emp), sizeof(emp))) {
        if (emp.empID == empID) {
            found = true;
            break;
        }
    }
    file.close();
    return found;
}

// Function to delete an employee record by ID
void deleteEmployeeByID(const string& filename, int empID) {
    fstream file;
    file.open(filename, ios::in | ios::binary);
    if (!file) {
        cerr << "Error in opening file!" << endl;
        return;
    }
    
    fstream tempFile;
    tempFile.open("temp.dat", ios::out | ios::binary);
    if (!tempFile) {
        cerr << "Error in opening temporary file!" << endl;
        file.close();
        return;
    }

    Employee emp;
    bool deleted = false;
    while (file.read(reinterpret_cast<char*>(&emp), sizeof(emp))) {
        if (emp.empID == empID) {
            deleted = true;
            cout << "Employee with ID " << empID << " has been deleted." << endl;
            continue; // Skip writing the employee to the temp file (effectively deleting it)
        }
        tempFile.write(reinterpret_cast<const char*>(&emp), sizeof(emp));
    }

    if (!deleted) {
        cout << "Employee with ID " << empID << " not found." << endl;
    }

    file.close();
    tempFile.close();

    // Replace the original file with the temp file
    remove(filename.c_str());
    rename("temp.dat", filename.c_str());
}

// Main function for user interaction
int main() {
    string filename = "employees.dat";
    int choice, empID;
    string name, designation;
    double salary;

    while (true) {
        cout << "\nEmployee Management System\n";
        cout << "1. Add Employee\n";
        cout << "2. Display Employee\n";
        cout << "3. Delete Employee\n";
        cout << "4. Exit\n";
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                cout << "\nEnter Employee ID: ";
                cin >> empID;
                cin.ignore();  // Ignore newline character after reading integer
                cout << "Enter Employee Name: ";
                getline(cin, name);
                cout << "Enter Designation: ";
                getline(cin, designation);
                cout << "Enter Salary: ";
                cin >> salary;
                
                Employee newEmp(empID, name, designation, salary);
                writeEmployeeData(filename, newEmp);
                cout << "Employee added successfully!" << endl;
                break;

            case 2:
                cout << "\nEnter Employee ID to display: ";
                cin >> empID;
                Employee emp;
                if (searchEmployeeByID(filename, empID, emp)) {
                    cout << "\nEmployee Found!" << endl;
                    displayEmployee(emp);
                } else {
                    cout << "Employee with ID " << empID << " not found." << endl;
                }
                break;

            case 3:
                cout << "\nEnter Employee ID to delete: ";
                cin >> empID;
                deleteEmployeeByID(filename, empID);
                break;

            case 4:
                cout << "Exiting the program." << endl;
                return 0;

            default:
                cout << "Invalid choice. Please try again." << endl;
        }
    }
}
