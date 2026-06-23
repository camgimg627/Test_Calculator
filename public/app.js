import { calculateLandTransferTax, formatMoney, provinces } from "./taxCalculator.mjs";

const form = document.querySelector("#calculator-form");
const provinceSelect = document.querySelector("#province");
const provinceTax = document.querySelector("#province-tax");
const municipalTax = document.querySelector("#municipal-tax");
const totalTax = document.querySelector("#total-tax");
const notesList = document.querySelector("#notes");

for (const province of provinces) {
  const option = document.createElement("option");
  option.value = province;
  option.textContent = province;
  if (province === "Ontario") {
    option.selected = true;
  }
  provinceSelect.append(option);
}

function readNumber(id) {
  const value = document.querySelector(id).value;
  return value === "" ? null : Number(value);
}

function render() {
  const result = calculateLandTransferTax({
    province: provinceSelect.value,
    city: document.querySelector("#city").value,
    purchasePrice: readNumber("#purchase-price"),
    nsRate: readNumber("#ns-rate"),
    nlRate: readNumber("#nl-rate"),
    isFirstTimeBuyer: document.querySelector("#first-time-buyer").checked,
    bcForeignBuyer: document.querySelector("#bc-foreign-buyer").checked,
    salePrice: readNumber("#sale-price"),
  });

  provinceTax.textContent = formatMoney(result.provinceTax);
  municipalTax.textContent = formatMoney(result.municipalTax);
  totalTax.textContent = formatMoney(result.totalTax);

  notesList.replaceChildren(
    ...result.notes.map((note) => {
      const item = document.createElement("li");
      item.textContent = note;
      return item;
    }),
  );
}

form.addEventListener("input", render);
form.addEventListener("change", render);
render();
