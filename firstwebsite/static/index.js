document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('appointment-form');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time');
    const restrictionMessage = document.getElementById('restriction-message');

    const availableTimes = [
        '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM'
    ];

    if (dateInput && timeSelect) {
        dateInput.addEventListener('input', function() {
            const selectedDate = dateInput.value;
            if (!selectedDate) return;

            fetch(`/appointments?date=${selectedDate}`)
                .then(response => response.json())
                .then(data => {
                    const bookedTimes = data.booked_times;
                    timeSelect.innerHTML = '<option value="" disabled selected>Select a time</option>';
                    availableTimes.forEach(time => {
                        const option = document.createElement('option');
                        option.value = time;
                        option.textContent = time;
                        if (bookedTimes.includes(time)) {
                            option.disabled = true;
                        }
                        timeSelect.appendChild(option);
                    });
                });
        });

        availableTimes.forEach(time => {
            const option = document.createElement('option');
            option.value = time;
            option.textContent = time;
            timeSelect.appendChild(option);
        });

        dateInput.addEventListener('input', function() {
            const selectedDate = new Date(dateInput.value);
            const dayOfWeek = selectedDate.getUTCDay();
            if (dayOfWeek === 0 || dayOfWeek === 6) {
                restrictionMessage.classList.remove('hidden');
                dateInput.setCustomValidity("Appointments cannot be scheduled on weekends.");
            } else {
                restrictionMessage.classList.add('hidden');
                dateInput.setCustomValidity("");
            }
        });
    }
    const editButton = document.getElementById('edit');
    const updateButton = document.getElementById('update');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const nameInput = document.getElementById('name');
    const gradeInput = document.getElementById('grade');

    editButton.addEventListener('click', () => {
        usernameInput.disabled = false;
        emailInput.disabled = false;
        nameInput.disabled = false;
        gradeInput.disabled = false;
        updateButton.disabled = false;
    });
});

    

