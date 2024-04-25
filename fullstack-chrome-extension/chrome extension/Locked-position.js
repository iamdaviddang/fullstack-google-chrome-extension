var storedData = null;
let visible = false;

// Funkce pro vytvoření tabulky s daty
function createDataTable(data) {
  // Pokud nejsou data k dispozici, vrátíme se
  if (!data) {
    console.error(
      "Chyba: Nejsou k dispozici žádná data pro vytvoření tabulky."
    );
    return;
  }

  // Vytvoření tabulky
  var table = document.createElement("table");
  table.className = "locked-positions";
  table.style.cssText =
    "position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: RGB(33, 37, 41); color: white; padding: 20px; border-collapse: collapse; border: 2px solid black; z-index: 9999;";

  // Vytvoření záhlaví tabulky
  var thead = table.createTHead();
  var headerRow = thead.insertRow();
  var headers = ["Position", "Remark", "Type"];
  headers.forEach(function (headerText) {
    var th = document.createElement("th");
    th.appendChild(document.createTextNode(headerText));
    th.style.cssText = "border: 1px solid white; padding: 10px;";
    headerRow.appendChild(th);
  });

  // Vytvoření těla tabulky s daty
  var tbody = table.createTBody();
  Object.keys(data).forEach(function (position) {
    var rowData = data[position];
    var row = tbody.insertRow();

    // Přidání sloupců pro pozici, poznámku a typ
    var cellPosition = row.insertCell();
    cellPosition.style.cssText = "border: 1px solid white; padding: 10px;";
    cellPosition.appendChild(document.createTextNode(position));

    var cellRemark = row.insertCell();
    cellRemark.style.cssText = "border: 1px solid white; padding: 10px;";
    cellRemark.appendChild(document.createTextNode(rowData.remark));

    var cellType = row.insertCell();
    cellType.style.cssText = "border: 1px solid white; padding: 10px;";
    cellType.appendChild(document.createTextNode(rowData.type));
  });

  // Přidání tlačítka pro zavření tabulky
  var closeButton = document.createElement("button");
  closeButton.appendChild(document.createTextNode("Zavřít"));
  closeButton.className = "btn btn-primary btn-padd top-left-button";
  closeButton.addEventListener("click", function () {
    table.remove();
    visible = false;
  });
  table.appendChild(closeButton);

  // Přidání tabulky do dokumentu
  document.body.appendChild(table);
}

// Funkce pro načtení dat z API
function fetchDataFromAPI() {
  return fetch("http://172.25.32.4/api/v2/monitor/get-data")
    .then((response) => response.json())
    .then((data) => {
      if (data && data.data && data.data.marked_positions_data) {
        storedData = data.data.marked_positions_data;
      } else {
        console.error(
          "Chyba: Data nebyla načtena z API nebo neobsahují položky v objektu marked_positions_data."
        );
      }
    })
    .catch((error) => {
      console.error("Chyba při načítání dat z API:", error);
    });
}

// Funkce pro zobrazení tabulky
function showDataTable() {
  if (storedData) {
    createDataTable(storedData);
    document.querySelector(".sb-sidenav-toggled").className =
      "sb-sidenav-toggled modal-open";
  } else {
    console.error(
      "Chyba: Nejsou k dispozici žádná data pro zobrazení tabulky."
    );
  }
}

// Funkce pro skrytí tabulky
function hideDataTable() {
  var table = document.querySelector(".locked-positions");
  if (table) {
    table.remove();
    document.querySelector("body").className = "sb-sidenav-toggled";
  } else {
    console.error("Chyba: Tabulka nebyla nalezena.");
  }
}

function toggleTable() {
  if (visible) {
    visible = false;
    hideDataTable();
  } else {
    visible = true;
    showDataTable();
  }
}

// Funkce pro přidání tlačítek na stránku
function addButtonsToPage() {
  var showButton = document.createElement("button");
  showButton.innerHTML = "Locked position";
  showButton.className = "btn btn-primary btn-padd top-left-button";
  showButton.addEventListener("click", toggleTable);

  var leftTopContainer = document.getElementById("leftTopContainer");
  if (leftTopContainer) {
    leftTopContainer.appendChild(showButton);
  } else {
    console.error("Chyba: Div s ID=leftTopContainer nebyl nalezen.");
  }
}

function hideCheckInButtons() {
  document.getElementById("checkinButton").style.display = "none";
  document.getElementById("CXcheckinButton").style.display = "none";
}

// Zavolání funkcí pro přidání tlačítek na stránku a načtení dat z API
addButtonsToPage();
fetchDataFromAPI();
hideCheckInButtons();
