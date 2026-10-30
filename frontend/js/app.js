'use strict';
// В основном режиме frontend и API обслуживает один FastAPI-сервер.
// Порт 5500 оставлен для необязательного отдельного frontend-сервера.
const API_BASE = location.port === '5500' ? 'http://127.0.0.1:8000' : '';
const state = {items: [], categories: [], searchQuery: '', selectedCategory: 'all', sortBy: 'name-asc', loading: false, busy: false, editingId: null, connected: false};
const $ = selector => document.querySelector(selector);
const cards = $('#cards'), modal = $('#modal'), form = $('#item-form');
const fieldLabels = {name:'Название', article:'Артикул', price:'Цена', description:'Описание', category_id:'Категория', parameter:'Характеристика', image_url:'Иллюстрация'};
let returnFocus = null;

async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(API_BASE + path, {...options, signal: controller.signal,
      headers: {...(options.body ? {'Content-Type':'application/json'} : {}), ...(options.headers || {})}});
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      const detail = Array.isArray(data.detail)
        ? data.detail.map(e => `${fieldLabels[e.loc?.[1]] || 'Данные'}: ${e.msg}`).join('; ')
        : data.detail;
      const error = new Error(detail || `Ошибка HTTP ${response.status}`);
      error.status = response.status;
      error.details = data.detail;
      throw error;
    }
    return response.status === 204 ? null : await response.json();
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Сервер не ответил за 10 секунд. Проверьте соединение и обновите каталог.');
    if (error instanceof TypeError) throw new Error('Не удалось связаться с сервером. Запустите backend и нажмите «Обновить с сервера».');
    throw error;
  } finally { clearTimeout(timer); }
}

function message(text, isError = false) {
  const area = $('#app-message');
  area.textContent = text;
  area.hidden = !text;
  area.classList.toggle('is-error', isError);
  area.setAttribute('role', isError ? 'alert' : 'status');
}

function filteredItems() {
  const q = state.searchQuery.trim().toLocaleLowerCase('ru');
  const items = state.items.filter(item => (state.selectedCategory === 'all' || item.category_id === Number(state.selectedCategory)) &&
    (!q || [item.name, item.article, item.description, item.category.name].some(value => value.toLocaleLowerCase('ru').includes(q))));
  return [...items].sort((a,b) => {
    if (state.sortBy === 'price-asc') return Number(a.price) - Number(b.price);
    if (state.sortBy === 'price-desc') return Number(b.price) - Number(a.price);
    return state.sortBy === 'name-desc' ? b.name.localeCompare(a.name, 'ru') : a.name.localeCompare(b.name, 'ru');
  });
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function makeCard(item) {
  const card = element('article', 'card');
  card.dataset.id = item.id;
  const img = element('img');
  img.src = API_BASE + item.image_url;
  img.alt = `Схематичное изображение: ${item.name}`;
  img.width = 320; img.height = 210;
  const body = element('div', 'card-body');
  const dl = element('dl');
  [['ID', item.id], ['Артикул', item.article], ['Параметр', item.parameter || 'Не указан']].forEach(([label, value]) => {
    const row = element('div'); row.append(element('dt', '', label), element('dd', '', value)); dl.append(row);
  });
  const price = element('p', 'price', `${Number(item.price).toLocaleString('ru-RU', {minimumFractionDigits:2, maximumFractionDigits:2})} ₽`);
  price.append(element('span', '', 'учебная цена'));
  const actions = element('div', 'card-actions');
  const edit = element('button', 'edit-button', 'Изменить'); edit.type='button'; edit.dataset.editId=item.id;
  edit.setAttribute('aria-label', `Изменить: ${item.name}`);
  const del = element('button', 'delete-button', 'Удалить'); del.type='button'; del.dataset.deleteId=item.id;
  del.setAttribute('aria-label', `Удалить: ${item.name}`);
  edit.disabled = del.disabled = state.busy || state.loading;
  actions.append(edit, del);
  body.append(element('p', 'category', item.category.name), element('h3', '', item.name), element('p', 'description', item.description), dl, price, actions);
  card.append(img, body);
  return card;
}

function render() {
  const items = filteredItems();
  cards.replaceChildren(...items.map(makeCard));
  cards.setAttribute('aria-busy', String(state.loading));
  $('#empty-state').hidden = items.length > 0 || state.loading || !state.connected;
  $('#catalog-count').textContent = `Показано: ${items.length} из ${state.items.length}`;
  $('#results-note').textContent = state.loading ? 'Загрузка данных…' : `Найдено позиций: ${items.length}`;
  $('#hero-count').textContent = `${String(state.items.length).padStart(2, '0')} деталей`;
  $('#hero-categories').textContent = `${new Set(state.items.map(item => item.category_id)).size} категорий`;
  $('#api-state').textContent = state.loading ? 'Загрузка с сервера…' : state.connected ? 'Данные получены из базы' : 'Нет связи с сервером';
  $('#api-state').classList.toggle('offline', !state.connected);
  $('#add-item-button').disabled = state.busy || state.loading || !state.connected;
  $('#reload-button').disabled = state.busy || state.loading;
}

function fillCategories() {
  const chosen = $('#category').value;
  $('#category').replaceChildren(new Option('Все категории','all'));
  $('#item-category').replaceChildren(new Option('Выберите категорию',''));
  state.categories.forEach(category => {
    $('#category').append(new Option(category.name, category.id));
    $('#item-category').append(new Option(category.name, category.id));
  });
  if ([...$('#category').options].some(o => o.value === chosen)) $('#category').value = chosen;
}

async function loadData() {
  if (state.loading || state.busy) return;
  state.loading = true; message(''); render();
  try {
    const [categories, items] = await Promise.all([api('/api/categories'), api('/api/parts')]);
    state.categories = categories; state.items = items; state.connected = true;
    fillCategories();
  } catch (error) { state.connected = false; message(error.message, true); }
  finally { state.loading = false; render(); }
}

function clearErrors() {
  form.querySelectorAll('.error').forEach(node => node.textContent = '');
  form.querySelectorAll('[aria-invalid]').forEach(node => node.removeAttribute('aria-invalid'));
}

function openModal(item = null) {
  form.reset(); clearErrors();
  state.editingId = item?.id ?? null;
  $('#modal-title').textContent = item ? 'Изменить запчасть' : 'Добавить запчасть';
  $('.modal-dialog .eyebrow').textContent = item ? `РЕДАКТИРОВАНИЕ · ID ${item.id}` : 'НОВАЯ ПОЗИЦИЯ';
  $('#save-button').textContent = item ? 'Сохранить изменения' : 'Сохранить деталь';
  if (item) Object.keys(fieldLabels).forEach(key => {form.elements[key].value = item[key];});
  returnFocus = document.activeElement;
  modal.hidden = false;
  document.body.classList.add('modal-open');
  document.querySelectorAll('header, main, footer').forEach(node => node.inert = true);
  $('#item-name').focus();
}

function closeModal() {
  if (state.busy) return;
  modal.hidden = true;
  document.body.classList.remove('modal-open');
  document.querySelectorAll('header, main, footer').forEach(node => node.inert = false);
  form.reset(); clearErrors();
  state.editingId = null;
  if (returnFocus?.isConnected) returnFocus.focus(); else $('#add-item-button').focus();
}

function validateField(input) {
  const error = form.querySelector(`[data-error-for="${input.name}"]`);
  if (!error) return true;
  const value = input.value.trim();
  let text = '';
  if (input.required && !value) text = 'Заполните это поле.';
  else if (input.minLength > 0 && value.length < input.minLength) text = `Минимум ${input.minLength} символов.`;
  else if (input.validity.rangeUnderflow || input.validity.rangeOverflow) text = `Цена от ${input.min} до ${input.max} ₽.`;
  else if (input.validity.stepMismatch) text = 'Укажите цену с точностью до копеек.';
  else if (input.validity.patternMismatch) text = 'Используйте буквы, цифры и дефис.';
  else if (!input.validity.valid) text = 'Проверьте значение поля.';
  error.textContent = text;
  input.setAttribute('aria-invalid', String(Boolean(text)));
  return !text;
}

$('#query').addEventListener('input', e => {state.searchQuery=e.target.value; render();});
$('#category').addEventListener('change', e => {state.selectedCategory=e.target.value; render();});
$('#sort').addEventListener('change', e => {state.sortBy=e.target.value; render();});
$('#reload-button').addEventListener('click', loadData);
$('#add-item-button').addEventListener('click', () => openModal());
document.addEventListener('click', e => {if (e.target.matches('[data-close-modal]')) closeModal();});
document.addEventListener('keydown', e => {
  if (modal.hidden) return;
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Tab') {
    const nodes = [...modal.querySelectorAll('button, input, select, textarea')].filter(node => !node.disabled);
    const first = nodes[0], last = nodes.at(-1);
    if (e.shiftKey && document.activeElement === first) {e.preventDefault(); last.focus();}
    else if (!e.shiftKey && document.activeElement === last) {e.preventDefault(); first.focus();}
  }
});

cards.addEventListener('click', async e => {
  const edit = e.target.closest('[data-edit-id]'), del = e.target.closest('[data-delete-id]');
  if ((!edit && !del) || state.busy || state.loading) return;
  const id = Number(edit?.dataset.editId || del.dataset.deleteId);
  if (del && !confirm(`Удалить «${state.items.find(item => item.id === id)?.name}» из базы данных?`)) return;
  state.busy = true; render(); message('');
  let selected = null;
  try {
    if (edit) selected = await api(`/api/parts/${id}`);
    else {
      await api(`/api/parts/${id}`, {method:'DELETE'});
      state.items = state.items.filter(item => item.id !== id);
      message('Запчасть удалена из базы данных.');
    }
  } catch (error) { message(error.message, true); }
  finally {state.busy=false; render();}
  if (selected) openModal(selected);
});

form.addEventListener('input', e => {if (e.target.matches('input,select,textarea')) validateField(e.target);});
form.addEventListener('submit', async e => {
  e.preventDefault();
  if (state.busy) return;
  clearErrors();
  const valid = [...form.querySelectorAll('input,select,textarea')].map(validateField).every(Boolean);
  if (!valid) {form.querySelector('[aria-invalid="true"]')?.focus(); return;}
  const data = Object.fromEntries(new FormData(form));
  data.category_id = Number(data.category_id);
  // Цена передаётся десятичной строкой, чтобы сервер разобрал её как Decimal.
  const editingId = state.editingId;
  state.busy = true; $('#save-button').disabled = true;
  form.setAttribute('aria-busy','true');
  // Блокируем поля после FormData, чтобы незавершённый запрос нельзя было изменить.
  form.querySelectorAll('input,select,textarea').forEach(node => node.disabled=true);
  let saved = false;
  try {
    const item = await api(editingId ? `/api/parts/${editingId}` : '/api/parts', {method: editingId ? 'PATCH' : 'POST', body: JSON.stringify(data)});
    state.items = editingId ? state.items.map(old => old.id === editingId ? item : old) : [...state.items, item];
    state.searchQuery=''; state.selectedCategory='all'; $('#query').value=''; $('#category').value='all';
    message(editingId ? 'Изменения сохранены в базе данных.' : `Запчасть создана в базе данных. ID: ${item.id}.`);
    saved = true;
  } catch (error) {
    $('#form-error').textContent = error.message;
    if (Array.isArray(error.details)) error.details.forEach(detail => {
      const node = form.querySelector(`[data-error-for="${detail.loc?.[1]}"]`);
      if (node) node.textContent = detail.msg;
    });
  } finally {
    state.busy=false; $('#save-button').disabled=false; form.removeAttribute('aria-busy');
    form.querySelectorAll('input,select,textarea').forEach(node => node.disabled=false);
    render();
  }
  if (saved) {closeModal(); location.hash='catalog';}
});
loadData();
