// Definir o mínimo da data para hoje
document.addEventListener('DOMContentLoaded', function () {
    const dataInput = document.getElementById('data');
    const hoje = new Date();
    const yyyy = hoje.getFullYear();
    const mm = String(hoje.getMonth() + 1).padStart(2, '0');
    const dd = String(hoje.getDate()).padStart(2, '0');
    dataInput.min = `${yyyy}-${mm}-${dd}`;
});

document.getElementById('agendamento-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const profissional = document.getElementById('profissional').value;
    const data = document.getElementById('data').value;
    const horario = document.getElementById('horario').value;
    const mensagemDiv = document.getElementById('mensagem');

    // Simulação de envio (não há backend real para agendamento)
    if (profissional && data && horario) {
        mensagemDiv.textContent = `Agendamento realizado com ${profissional.charAt(0).toUpperCase() + profissional.slice(1)} em ${data} às ${horario}.`;
        mensagemDiv.className = 'sucesso';
        this.reset();
    } else {
        mensagemDiv.textContent = 'Por favor, preencha todos os campos.';
        mensagemDiv.className = 'erro';
    }
});