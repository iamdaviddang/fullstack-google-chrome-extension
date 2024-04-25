// CSS styly
var css = `
.ip-window {
  display: none;
  background-color: RGB(33, 37, 41);
  width: 400px;
  height: 300px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 30px;
  padding: 20px;
  border: 1px solid black;
  z-index: 999;
}

.ip-window h2 {
  text-align: center;
  font-weight: bold;
  font-size: 30px;
  margin-bottom: 20px;
  color: white;
}

form {
  text-align: center;
}

form label {
  font-weight: bold;
  font-size: 20px;
}

form input {
  width: 100%;
  margin: 10px 0;
  padding: 10px 15px;
  border-radius: 10px;
  border: none;
}

form input::placeholder {
  text-align: center;
}

form input[type="submit"] {
  background-color: green;
  color: white;
  font-weight: bold;
  width: 50%;
  cursor: pointer;
}

form input[type="button"] {
  background-color: red;
  color: white;
  font-weight: bold;
  width: 50%;
  cursor: pointer;
}


.overlayTableIP {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Průhledný černý prvek */
  z-index: 998; /* Nastavení vrchní vrstvy */
}
`;

// Vytvoření stylu
var style = document.createElement("style");
style.type = "text/css";
if (style.styleSheet) {
  style.styleSheet.cssText = css;
} else {
  style.appendChild(document.createTextNode(css));
}
document.getElementsByTagName("head")[0].appendChild(style);

// Vytvoření divu s formulářem
var divIP = document.createElement("div");
divIP.className = "ip-window";
divIP.innerHTML = `
  <h2>IP Finder</h2>
  <hr style="height:2px;border-width:0;color:gray;background-color:gray">
  <form id="ipForm">
    <input type="text" id="inputUSNIP" name="inputUSN" placeholder="USN">
    <input type="submit" value="Submit" id="submitButtonIP">
    <input type="button" value="Cancel" id="cancelButtonIP">
  </form>
  <div class="loadingIP" style="display: none;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid" width="100"
                height="100" style="shape-rendering: auto; display: block; background: transparent;"
                xmlns:xlink="http://www.w3.org/1999/xlink">
                <g>
                    <path fill="none" stroke="#e90c0c" stroke-width="8"
                        stroke-dasharray="42.76482137044271 42.76482137044271"
                        d="M24.3 30C11.4 30 5 43.3 5 50s6.4 20 19.3 20c19.3 0 32.1-40 51.4-40 C88.6 30 95 43.3 95 50s-6.4 20-19.3 20C56.4 70 43.6 30 24.3 30z"
                        stroke-linecap="round" style="transform:scale(0.8);transform-origin:50px 50px">
                        <animate attributeName="stroke-dashoffset" repeatCount="indefinite" dur="1s" keyTimes="0;1"
                            values="0;256.58892822265625"></animate>
                    </path>
                    <g></g>
                </g><!-- [ldio] generated by https://loading.io -->
            </svg>
            <p style="color: white">Working, please wait..</p>
        </div>
`;
document.body.appendChild(divIP);

// Funkce pro odeslání formuláře
async function submitForm(event) {
  try {
    event.preventDefault();
    var usnValue = document.getElementById("inputUSNIP").value;
    showLoading();
    // API call
    const response = await fetch(
      `http://10.82.66.179:8080/api/ipfinder/${usnValue}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    hideLoading();
    // Zpracování odpovědi z API callu
    const data = await response.json();
    // Zobrazení response z API callu jako alertu
    alert(JSON.stringify(data));
    // Skrytí formuláře po odeslání
    document.getElementById("inputUSNIP").value = "";
    divIP.style.display = "none";
    document
      .querySelector(".overlayTableIP")
      .parentNode.removeChild(document.querySelector(".overlayTableIP"));
  } catch (error) {
    // Zpracování chyb
    console.error("Chyba při zpracování požadavku:", error);
    // Zobrazení alertu s chybou
    alert("Došlo k chybě při zpracování požadavku.");
  }
}

// Funkce pro zobrazeni loadingu
function showLoading() {
  document.querySelector("#cancelButtonIP").style.display = "none";
  document.querySelector("#submitButtonIP").style.display = "none";
  document.querySelector(".loadingIP").style.cssText =
    "display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;";
}

// Funkce pro schovani loadingu
function hideLoading() {
  document.querySelector("#cancelButtonIP").style.display = "inline-block";
  document.querySelector("#submitButtonIP").style.display = "inline-block";
  document.querySelector(".loadingIP").style.display = "none";
}

// Funkce pro skrytí formuláře
document
  .getElementById("cancelButtonIP")
  .addEventListener("click", function () {
    document.getElementById("inputUSNIP").value = "";
    divIP.style.display = "none";
    document
      .querySelector(".overlayTableIP")
      .parentNode.removeChild(document.querySelector(".overlayTableIP"));
  });

// Přidání event listeneru pro odeslání formuláře
document.getElementById("ipForm").addEventListener("submit", submitForm);

// Funkce pro zobrazení formuláře po kliknutí na tlačítko
function openFormIP() {
  const divZtmavnuti = document.createElement("div");
  divZtmavnuti.classList.add("overlayTableIP");
  divZtmavnuti.style.display = "block";
  document.body.appendChild(divZtmavnuti);
  divIP.style.display = "block";
}

// Vytvoření tlačítka pro otevření formuláře
var buttonIP = document.createElement("button");
buttonIP.innerHTML = "IP finder";
buttonIP.className = "btn btn-primary btn-padd top-left-button IP";
// Přidání event listeneru pro otevření formuláře po kliknutí na tlačítko
buttonIP.addEventListener("click", openFormIP);

// Přidání tlačítka na začátek stránky
document.getElementById("leftTopContainer").appendChild(buttonIP);
