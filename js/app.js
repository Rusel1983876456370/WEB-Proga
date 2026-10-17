"use strict";

const STORAGE_KEY = "autodetal-items-v2";

const categoryLabels = {
  engine: "Двигатель",
  brakes: "Тормоза",
  ignition: "Зажигание",
  suspension: "Подвеска",
  drive: "Привод",
  other: "Другое",
};

const defaults = [
  {
    id: "AP-FL-001",
    name: "Масляный фильтр",
    category: "engine",
    categoryLabel: "Двигатель",
    description: "Задерживает загрязнения в системе смазки двигателя.",
    article: "AP-FL-001",
    parameter: "Резьба M20 × 1,5",
    price: 490,
    image: "filter.svg",
  },
  {
    id: "AP-BR-002",
    name: "Тормозной диск",
    category: "brakes",
    categoryLabel: "Тормоза",
    description: "Рабочая поверхность для торможения колеса колодками.",
    article: "AP-BR-002",
    parameter: "Диаметр 280 мм",
    price: 3200,
    image: "brake.svg",
  },
  {
    id: "AP-IG-003",
    name: "Свеча зажигания",
    category: "ignition",
    categoryLabel: "Зажигание",
    description:
      "Создаёт искру для воспламенения смеси в бензиновом двигателе.",
    article: "AP-IG-003",
    parameter: "Резьба M14 × 1,25",
    price: 650,
    image: "plug.svg",
  },
  {
    id: "AP-FL-004",
    name: "Воздушный фильтр",
    category: "engine",
    categoryLabel: "Двигатель",
    description: "Очищает воздух перед поступлением во впускную систему.",
    article: "AP-FL-004",
    parameter: "Размер 250 × 180 мм",
    price: 890,
    image: "air.svg",
  },
  {
    id: "AP-SU-005",
    name: "Амортизатор",
    category: "suspension",
    categoryLabel: "Подвеска",
    description:
      "Гасит колебания кузова и помогает колесу сохранять контакт с дорогой.",
    article: "AP-SU-005",
    parameter: "Тип: газомасляный",
    price: 4500,
    image: "shock.svg",
  },
  {
    id: "AP-DR-006",
    name: "Поликлиновой ремень",
    category: "drive",
    categoryLabel: "Привод",
    description: "Передаёт вращение от двигателя к навесным агрегатам.",
    article: "AP-DR-006",
    parameter: "Профиль 6PK, длина 1050 мм",
    price: 1100,
    image: "belt.svg",
  },
];

const state = {
  items: loadItems(),
  searchQuery: "",
  selectedCategory: "all",
  sortBy: "name-asc",
};

const $ = (selector) => document.querySelector(selector);

const cards = $("#cards");
const emptyState = $("#empty-state");
const modal = $("#modal");
const form = $("#item-form");

function loadItems() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    return saved ? JSON.parse(saved) : structuredClone(defaults);
  } catch {
    return structuredClone(defaults);
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.items));
}

function filteredItems() {
  const query = state.searchQuery.trim().toLowerCase();

  const list = state.items.filter((item) => {
    const matchesCategory =
      state.selectedCategory === "all" ||
      item.category === state.selectedCategory;

    const matchesSearch =
      !query ||
      [
        item.name,
        item.article,
        item.description,
        item.categoryLabel,
      ].some((value) =>
        String(value).toLowerCase().includes(query),
      );

    return matchesCategory && matchesSearch;
  });

  return [...list].sort((a, b) => {
    if (state.sortBy === "price-asc") {
      return a.price - b.price;
    }

    if (state.sortBy === "price-desc") {
      return b.price - a.price;
    }

    if (state.sortBy === "name-desc") {
      return b.name.localeCompare(a.name, "ru");
    }

    return a.name.localeCompare(b.name, "ru");
  });
}

function makeCard(item) {
  const article = document.createElement("article");
  article.className = "card";
  article.dataset.id = item.id;

  const image = document.createElement("img");
  image.src = `assets/images/${item.image || "filter.svg"}`;
  image.alt = `Схематичное изображение: ${item.name}`;
  image.width = 320;
  image.height = 210;

  const body = document.createElement("div");
  body.className = "card-body";

  const category = document.createElement("p");
  category.className = "category";
  category.textContent = item.categoryLabel;

  const title = document.createElement("h3");
  title.textContent = item.name;

  const description = document.createElement("p");
  description.className = "description";
  description.textContent = item.description;

  const details = document.createElement("dl");

  const detailRows = [
    ["Артикул", item.article],
    ["Категория", item.categoryLabel],
    ["Параметр", item.parameter || "Добавлено пользователем"],
  ];

  detailRows.forEach(([term, value]) => {
    const row = document.createElement("div");

    const dt = document.createElement("dt");
    dt.textContent = term;

    const dd = document.createElement("dd");
    dd.textContent = value;

    row.append(dt, dd);
    details.append(row);
  });

  const price = document.createElement("p");
  price.className = "price";
  price.textContent = `${Number(item.price).toLocaleString("ru-RU")} ₽`;

  const priceNote = document.createElement("span");
  priceNote.textContent = "учебная цена";

  price.append(priceNote);

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete-button";
  deleteButton.type = "button";
  deleteButton.dataset.deleteId = item.id;
  deleteButton.textContent = "Удалить";

  body.append(
    category,
    title,
    description,
    details,
    price,
    deleteButton,
  );

  article.append(image, body);

  return article;
}

function render() {
  const items = filteredItems();

  cards.replaceChildren(...items.map(makeCard));

  emptyState.hidden = items.length > 0;

  $("#catalog-count").textContent =
    `Показано: ${items.length} из ${state.items.length}`;

  $("#results-note").textContent = items.length
    ? `Найдено позиций: ${items.length}`
    : "По вашему запросу позиций нет";

  $("#hero-count").textContent =
    `${state.items.length.toString().padStart(2, "0")} деталей`;

  $("#hero-categories").textContent =
    `${new Set(state.items.map((item) => item.category)).size} категорий`;
}

function fillCategories() {
  const categories = [
    "engine",
    "brakes",
    "ignition",
    "suspension",
    "drive",
    "other",
  ];

  categories.forEach((key) => {
    const option = document.createElement("option");

    option.value = key;
    option.textContent = categoryLabels[key];

    $("#category").append(option);

    const formOption = option.cloneNode(true);
    $("#item-category").append(formOption);
  });
}

function openModal() {
  modal.hidden = false;
  document.body.classList.add("modal-open");

  $("#item-name").focus();
}

function closeModal() {
  modal.hidden = true;
  document.body.classList.remove("modal-open");

  form.reset();

  document
    .querySelectorAll(".error")
    .forEach((error) => {
      error.textContent = "";
    });
}

function validateField(input) {
  const error = $(`[data-error-for="${input.name}"]`);

  let message = "";

  if (input.validity.valueMissing) {
    message = "Заполните это поле.";
  } else if (input.validity.tooShort) {
    message = `Минимум ${input.minLength} символа.`;
  } else if (
    input.validity.rangeUnderflow ||
    input.validity.rangeOverflow
  ) {
    message = `Введите цену от ${input.min} до ${input.max} ₽.`;
  } else if (input.validity.patternMismatch) {
    message = "Используйте буквы, цифры и дефис.";
  }

  error.textContent = message;

  input.setAttribute(
    "aria-invalid",
    message ? "true" : "false",
  );

  return !message;
}

$("#query").addEventListener("input", (event) => {
  state.searchQuery = event.target.value;
  render();
});

$("#category").addEventListener("change", (event) => {
  state.selectedCategory = event.target.value;
  render();
});

$("#sort").addEventListener("change", (event) => {
  state.sortBy = event.target.value;
  render();
});

$("#add-item-button").addEventListener("click", openModal);

document.addEventListener("click", (event) => {
  if (event.target.matches("[data-close-modal]")) {
    closeModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !modal.hidden) {
    closeModal();
  }
});

cards.addEventListener("click", (event) => {
  const button = event.target.closest("[data-delete-id]");

  if (!button) {
    return;
  }

  const id = button.dataset.deleteId;

  state.items = state.items.filter((item) => item.id !== id);

  persist();
  render();
});

form.addEventListener("input", (event) => {
  if (event.target.matches("input, select, textarea")) {
    validateField(event.target);
  }
});

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const inputs = [
    ...form.querySelectorAll("input, select, textarea"),
  ];

  const isValid = inputs.every(validateField);

  if (!isValid) {
    return;
  }

  const data = new FormData(form);
  const category = data.get("category");

  state.items.push({
    id: `USER-${Date.now()}`,
    name: data.get("name"),
    category,
    categoryLabel: categoryLabels[category],
    description: data.get("description"),
    article: data.get("article").toUpperCase(),
    parameter: "Добавлено пользователем",
    price: Number(data.get("price")),
    image: "filter.svg",
  });

  persist();
  render();
  closeModal();

  document.location.hash = "catalog";
});

fillCategories();
render();