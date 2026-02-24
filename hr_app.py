#!/usr/bin/env python3
"""Terminal HR solution for attendance and payroll tracking."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, asdict
from pathlib import Path

DATA_FILE = Path("hr_data.json")


@dataclass
class Employee:
    emp_id: str
    name: str
    hourly_rate: float


@dataclass
class AttendanceRecord:
    emp_id: str
    date: str
    hours: float


class HRApp:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self.data = {"employees": [], "attendance": []}
        self.load_data()

    def load_data(self) -> None:
        if self.data_file.exists():
            with self.data_file.open("r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save_data(self) -> None:
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def add_employee(self) -> None:
        print("\n--- Add Employee ---")
        emp_id = input("Employee ID: ").strip()
        if self.get_employee(emp_id):
            print("Employee ID already exists.")
            return

        name = input("Name: ").strip()
        rate = self.prompt_float("Hourly rate: ")

        employee = Employee(emp_id=emp_id, name=name, hourly_rate=rate)
        self.data["employees"].append(asdict(employee))
        self.save_data()
        print(f"Employee {name} added.")

    def list_employees(self) -> None:
        print("\n--- Employees ---")
        employees = self.data["employees"]
        if not employees:
            print("No employees found.")
            return

        for emp in employees:
            print(
                f"ID: {emp['emp_id']} | Name: {emp['name']} | "
                f"Rate: ${emp['hourly_rate']:.2f}/hr"
            )

    def mark_attendance(self) -> None:
        print("\n--- Mark Attendance ---")
        emp_id = input("Employee ID: ").strip()
        employee = self.get_employee(emp_id)
        if not employee:
            print("Employee not found.")
            return

        date = input("Date (YYYY-MM-DD, blank=today): ").strip() or dt.date.today().isoformat()
        if not self.valid_date(date):
            print("Invalid date format.")
            return

        hours = self.prompt_float("Hours worked: ")

        record = AttendanceRecord(emp_id=emp_id, date=date, hours=hours)
        self.data["attendance"].append(asdict(record))
        self.save_data()
        print(f"Attendance recorded for {employee['name']} on {date}.")

    def view_attendance(self) -> None:
        print("\n--- Attendance ---")
        records = self.data["attendance"]
        if not records:
            print("No attendance records found.")
            return

        for rec in records:
            employee = self.get_employee(rec["emp_id"])
            name = employee["name"] if employee else "Unknown"
            print(
                f"Date: {rec['date']} | ID: {rec['emp_id']} | "
                f"Name: {name} | Hours: {rec['hours']:.2f}"
            )

    def payroll_report(self) -> None:
        print("\n--- Payroll Report ---")
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()

        if not (self.valid_date(start) and self.valid_date(end)):
            print("Invalid date format.")
            return

        start_date = dt.date.fromisoformat(start)
        end_date = dt.date.fromisoformat(end)
        if start_date > end_date:
            print("Start date cannot be after end date.")
            return

        totals: dict[str, float] = {}
        for rec in self.data["attendance"]:
            rec_date = dt.date.fromisoformat(rec["date"])
            if start_date <= rec_date <= end_date:
                totals[rec["emp_id"]] = totals.get(rec["emp_id"], 0.0) + rec["hours"]

        if not totals:
            print("No attendance data in this date range.")
            return

        grand_total = 0.0
        for emp_id, total_hours in totals.items():
            emp = self.get_employee(emp_id)
            if not emp:
                continue
            pay = total_hours * float(emp["hourly_rate"])
            grand_total += pay
            print(
                f"ID: {emp_id} | Name: {emp['name']} | "
                f"Hours: {total_hours:.2f} | Pay: ${pay:.2f}"
            )

        print(f"\nTotal payroll expense: ${grand_total:.2f}")

    def get_employee(self, emp_id: str) -> dict | None:
        for emp in self.data["employees"]:
            if emp["emp_id"] == emp_id:
                return emp
        return None

    @staticmethod
    def valid_date(value: str) -> bool:
        try:
            dt.date.fromisoformat(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def prompt_float(prompt_text: str) -> float:
        while True:
            value = input(prompt_text).strip()
            try:
                parsed = float(value)
                if parsed < 0:
                    print("Please enter a non-negative value.")
                    continue
                return parsed
            except ValueError:
                print("Please enter a valid number.")

    def run(self) -> None:
        menu = {
            "1": self.add_employee,
            "2": self.list_employees,
            "3": self.mark_attendance,
            "4": self.view_attendance,
            "5": self.payroll_report,
        }

        while True:
            print("\n=== HR Solution App ===")
            print("1) Add employee")
            print("2) List employees")
            print("3) Mark attendance")
            print("4) View attendance")
            print("5) Generate payroll report")
            print("6) Exit")
            choice = input("Choose an option: ").strip()

            if choice == "6":
                print("Goodbye!")
                break

            action = menu.get(choice)
            if action:
                action()
            else:
                print("Invalid option. Please choose from 1 to 6.")


if __name__ == "__main__":
    HRApp().run()
