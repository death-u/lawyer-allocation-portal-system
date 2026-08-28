function switchTab(tab) {
        const lawyerForm = document.getElementById('form-lawyer');
        const clientForm = document.getElementById('form-client');
        const lawyerTab = document.getElementById('tab-lawyer');
        const clientTab = document.getElementById('tab-client');

        if (tab === 'lawyer') {
            // Show Lawyer Form, Hide Client Form
            lawyerForm.classList.remove('hidden');
            clientForm.classList.add('hidden');
            
            // Update Tab Styles
            lawyerTab.classList.add('tab-active');
            lawyerTab.classList.remove('tab-inactive');
            clientTab.classList.add('tab-inactive');
            clientTab.classList.remove('tab-active');
        } else {
            // Show Client Form, Hide Lawyer Form
            clientForm.classList.remove('hidden');
            lawyerForm.classList.add('hidden');
            
            // Update Tab Styles
            clientTab.classList.add('tab-active');
            clientTab.classList.remove('tab-inactive');
            lawyerTab.classList.add('tab-inactive');
            lawyerTab.classList.remove('tab-active');
        }
    }


function confirmPassword(value1, value2, el) {
    if (typeof el === "string") el = document.getElementById(el);
    if (!el) return;

    el.style.border = value1 !== value2 ? "1px solid red" : "1px solid green";
}