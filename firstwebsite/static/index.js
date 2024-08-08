document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('appointment-form');
    const dateInput = document.getElementById('date');
    const timeSelect = document.getElementById('time');
    const restrictionMessage = document.getElementById('restriction-message');

    const availableTimes = [
        '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM'
    ];

    if (dateInput && timeSelect && restrictionMessage) {
        dateInput.addEventListener('input', function() {
            const selectedDate = dateInput.value;
            if (!selectedDate) return;

            const currentDate = new Date();
            const selectedDateObj = new Date(selectedDate);

            let currentTime = null;
            if (selectedDateObj.toDateString() === currentDate.toDateString()) {
                currentTime = currentDate;
            }

            if (selectedDateObj < currentDate.setHours(0, 0, 0, 0)) {
                restrictionMessage.textContent = "You cannot select a past date.";
                restrictionMessage.classList.remove('hidden');
                dateInput.setCustomValidity("You cannot select a past date.");
                timeSelect.disabled = true;
                return;
            } else {
                restrictionMessage.classList.add('hidden');
                dateInput.setCustomValidity("");
                timeSelect.disabled = false;
            }

            fetch(`/appointments?date=${selectedDate}`)
                .then(response => response.json())
                .then(data => {
                    const bookedTimes = data.booked_times;
                    timeSelect.innerHTML = '<option value="" disabled selected>Select a time</option>';
                    availableTimes.forEach(time => {
                        const option = document.createElement('option');
                        option.value = time;
                        option.textContent = time;

                        const [hours, minutes, period] = time.match(/(\d+):(\d+) (\w+)/).slice(1);
                        let timeDate = new Date(selectedDateObj);
                        timeDate.setHours(period === 'PM' ? parseInt(hours) + 12 : parseInt(hours));
                        timeDate.setMinutes(minutes);

                        if (bookedTimes.includes(time) || (currentTime && timeDate < currentTime)) {
                            option.disabled = true;
                        }

                        timeSelect.appendChild(option);
                    });
                });
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

        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    const editButton = document.getElementById('edit');
    const updateButton = document.getElementById('update');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const nameInput = document.getElementById('name');
    const gradeInput = document.getElementById('grade');

    if (editButton) {
        editButton.addEventListener('click', () => {
            if (usernameInput) usernameInput.disabled = false;
            if (emailInput) emailInput.disabled = false;
            if (nameInput) nameInput.disabled = false;
            if (gradeInput) gradeInput.disabled = false;
            if (updateButton) updateButton.disabled = false;
        });
    }

    // Reschedule functionality
    const rescheduleButtons = document.querySelectorAll(".reschedule-button");

    if (rescheduleButtons) {
        rescheduleButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const form = event.target.closest('form');
                form.submit();
            });
        });
    }
});
