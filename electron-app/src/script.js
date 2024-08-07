const input = document.getElementById("fileInput");
const selectedFileName = document.getElementById('selectedFileName')

function selecionarArquivo(){
    const arquivo = input.files[0];

    if (arquivo){
        const extensao = arquivo.name.split('.').pop().toLowerCase();
        if (extensao === 'xlsx' || extensao === 'xls'){
            selectedFileName.textContent = arquivo.name;
        } else {
            alert("Por favor, selecione um arquivo xlsx ou xls.")
            input.value = '';
        }
} else {
    selectedFileName.textContent = 'Nenhum arquivo selecionado';
}
}

input.addEventListener('change', selecionarArquivo);
