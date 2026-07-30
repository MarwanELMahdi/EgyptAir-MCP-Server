INSERT INTO Employees (full_name, email, role, department, password)
VALUES
('Ahmed Hassan', 'ahmed@egyptair.com', 'CustomerService', 'Customer Service', 'pass123'),
('Sara Mohamed', 'sara@egyptair.com', 'Supervisor', 'Customer Service', 'pass123'),
('Omar Ali', 'omar@egyptair.com', 'Manager', 'Operations', 'pass123');  


INSERT INTO Flights
(flight_number, origin, destination, departure_time, arrival_time, status, delay_minutes)
VALUES
('MS701', 'Cairo', 'London', '2026-08-01 09:00', '2026-08-01 14:00', 'Scheduled', 0),
('MS702', 'Cairo', 'Paris', '2026-08-01 10:00', '2026-08-01 13:30', 'Delayed', 120),
('MS703', 'Cairo', 'Dubai', '2026-08-01 12:00', '2026-08-01 16:00', 'Cancelled', 0);


INSERT INTO Passengers
(full_name, passport_number, email, phone)
VALUES
('John Smith', 'P123456', 'john@example.com', '01234567890'),
('Emma Brown', 'P654321', 'emma@example.com', '01111111111'),
('Ali Hassan', 'P789456', 'ali@example.com', '01022222222'),
('Mona Ahmed', 'P456789', 'mona@example.com', '01533333333'),
('David Lee', 'P852963', 'david@example.com', '01299999999');


INSERT INTO Bookings
(passenger_id, flight_id, seat_number, ticket_class, booking_status)
VALUES
(1, 1, '12A', 'Economy', 'Confirmed'),
(2, 2, '8C', 'Business', 'Confirmed'),
(3, 2, '15F', 'Economy', 'Confirmed'),
(4, 3, '3A', 'First', 'Confirmed'),
(5, 1, '22D', 'Economy', 'Confirmed');


INSERT INTO CompensationRequests
(booking_id, requested_amount, reason, status, approved_by, created_at)
VALUES
(2, 250.00, 'Flight delayed more than 2 hours', 'Pending', NULL, '2026-08-01'),
(3, 180.00, 'Flight delayed', 'Approved', 2, '2026-08-01'),
(4, 400.00, 'Flight cancelled', 'Rejected', 3, '2026-08-01');


INSERT INTO Policies
(title, content)
VALUES

(
'Flight Delay Compensation Policy',

'Passengers delayed more than 2 hours may be eligible for compensation depending on the route and ticket conditions.'
),

(
'Baggage Policy',

'Each Economy passenger may carry one checked bag up to 23kg.'
),

(
'Rebooking Policy',

'Passengers on cancelled flights may request free rebooking to the next available flight.'
);


INSERT INTO Reports
(employee_id, report_type, status, progress, generated_at)
VALUES
(2, 'Daily Delay Report', 'Pending', 0, '2026-08-01');