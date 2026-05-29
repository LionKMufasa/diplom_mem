import fs from "node:fs/promises";
import path from "node:path";

import {
  ensureArtifactToolWorkspace,
  importArtifactTool,
  createSlideContext,
} from "file:///C:/Users/egork/.codex/plugins/cache/openai-primary-runtime/presentations/26.521.10419/skills/presentations/scripts/artifact_tool_utils.mjs";

const WORKSPACE = "C:/Users/egork/Desktop/coppelia_dpilom/outputs/019e65ab-8c32-77e2-b8f4-91937a9229fd/presentations/vkr-defense-17-slides";
const SOURCE_PPTX = "C:/Users/egork/Desktop/coppelia_dpilom/вкр/НИРС(7сем)/Презентация НИРС 2025 Миронов Егор Максимович.pptx";
const FINAL_PPTX = "C:/Users/egork/Desktop/coppelia_dpilom/вкр/Презентация ВКР 2026 Миронов Егор Максимович.pptx";
const PREVIEW_DIR = path.join(WORKSPACE, "final-preview");

const ASSETS = {
  cellScheme: "C:/Users/egork/Desktop/coppelia_dpilom/вкр/НИРС(7сем)/Схемы и рисунки/Схема роботизированной ячейки.png",
  torque: "C:/Users/egork/Desktop/coppelia_dpilom/reports/figures/vkr_practice_png/torque_rms_by_axis.png",
  hi: "C:/Users/egork/Desktop/coppelia_dpilom/reports/figures/vkr_practice_png/hi_curves_motor1.png",
  rul: "C:/Users/egork/Desktop/coppelia_dpilom/reports/figures/vkr_practice_png/rul_nn_actual_predicted_s3_motor1.png",
  dashboard: "C:/Users/egork/Desktop/coppelia_dpilom/reports/figures/vkr_practice_png/pak_dashboard_summary.png",
};

const colors = {
  dark: "#052A35",
  teal: "#176D82",
  card: "#F7FBFC",
  card2: "#EAF5F8",
  ink: "#062B35",
  muted: "#5D7480",
  blue: "#3369C7",
  orange: "#D96C3D",
  green: "#2D9A6A",
  white: "#FFFFFF",
};

function textOf(element) {
  return element?.text?.plainText || element?.text?.toString?.() || "";
}

function textElements(slide) {
  return slide.elements.items.filter((element) => textOf(element).trim().length > 0);
}

function setText(element, text, options = {}) {
  element.text = text;
  if (options.fontSize) element.text.fontSize = options.fontSize;
  if (options.color) element.text.color = options.color;
  if (options.bold !== undefined) element.text.bold = options.bold;
  if (options.align) element.text.alignment = options.align;
  if (options.valign) element.text.verticalAlignment = options.valign;
  if (options.typeface) element.text.typeface = options.typeface;
  if (options.insets) element.text.insets = options.insets;
}

function titleElement(slide) {
  const candidates = textElements(slide).filter((element) => {
    const frame = element.frame || {};
    const text = textOf(element).trim();
    return text && frame.top < 280 && frame.width > 250;
  });
  candidates.sort((a, b) => ((b.frame?.width || 0) * (b.frame?.height || 0)) - ((a.frame?.width || 0) * (a.frame?.height || 0)));
  return candidates[0] || textElements(slide)[0];
}

function setTitle(slide, title, options = {}) {
  const element = titleElement(slide);
  if (!element) return;
  setText(element, title, {
    fontSize: options.fontSize || 42,
    color: options.color || colors.white,
    bold: false,
    typeface: "Aptos Display",
    insets: { left: 0, right: 0, top: 0, bottom: 0 },
  });
}

function replaceWithTopTitle(ctx, slide, title, options = {}) {
  const oldTitle = titleElement(slide);
  if (oldTitle) oldTitle.delete();
  ctx.addText(slide, {
    x: options.x || 84,
    y: options.y || 64,
    width: options.width || 1020,
    height: options.height || 72,
    text: title,
    fontSize: options.fontSize || 42,
    color: options.color || colors.white,
    typeface: "Aptos Display",
  });
}

function deleteTextExceptTitle(slide) {
  const keep = titleElement(slide);
  for (const element of [...textElements(slide)]) {
    if (element !== keep) element.delete();
  }
}

function deleteImages(slide) {
  for (const image of [...slide.images.items]) image.delete();
}

function addBodyTitle(ctx, slide, text, x, y, w) {
  return ctx.addText(slide, {
    x,
    y,
    width: w,
    height: 34,
    text,
    fontSize: 20,
    color: colors.blue,
    bold: true,
    typeface: "Aptos",
  });
}

function addBodyText(ctx, slide, text, x, y, w, h, options = {}) {
  return ctx.addText(slide, {
    x,
    y,
    width: w,
    height: h,
    text,
    fontSize: options.fontSize || 18,
    color: options.color || colors.ink,
    bold: options.bold || false,
    typeface: "Aptos",
    insets: options.insets || { left: 0, right: 0, top: 0, bottom: 0 },
    fill: options.fill || "#00000000",
  });
}

function addCard(ctx, slide, x, y, w, h, title, lines, options = {}) {
  ctx.addShape(slide, {
    x,
    y,
    width: w,
    height: h,
    fill: options.fill || colors.card,
    line: { style: "solid", fill: options.line || "#CDE5EC", width: 1.2 },
  });
  ctx.addShape(slide, {
    x,
    y,
    width: 7,
    height: h,
    fill: options.accent || colors.blue,
    line: { style: "solid", fill: options.accent || colors.blue, width: 0 },
  });
  addBodyTitle(ctx, slide, title, x + 22, y + 18, w - 44);
  addBodyText(ctx, slide, lines.join("\n"), x + 22, y + 58, w - 42, h - 68, {
    fontSize: options.fontSize || 17,
    color: options.color || colors.ink,
  });
}

function addMetric(ctx, slide, x, y, w, h, value, label, options = {}) {
  ctx.addShape(slide, {
    x,
    y,
    width: w,
    height: h,
    fill: options.fill || colors.card,
    line: { style: "solid", fill: "#CDE5EC", width: 1.1 },
  });
  ctx.addText(slide, {
    x: x + 18,
    y: y + 16,
    width: w - 36,
    height: 38,
    text: value,
    fontSize: options.valueSize || 28,
    color: options.accent || colors.orange,
    bold: true,
    typeface: "Aptos Display",
  });
  ctx.addText(slide, {
    x: x + 18,
    y: y + 58,
    width: w - 36,
    height: h - 66,
    text: label,
    fontSize: options.labelSize || 15,
    color: colors.ink,
    typeface: "Aptos",
  });
}

function addBullets(ctx, slide, x, y, w, h, bullets, options = {}) {
  addBodyText(ctx, slide, bullets.map((item) => `• ${item}`).join("\n"), x, y, w, h, {
    fontSize: options.fontSize || 20,
    color: options.color || colors.white,
    fill: options.fill || "#00000000",
    insets: options.insets || { left: 0, right: 0, top: 0, bottom: 0 },
  });
}

function addFlow(ctx, slide, x, y, items) {
  const cardW = 240;
  const gap = 34;
  items.forEach((item, index) => {
    const cx = x + index * (cardW + gap);
    addCard(ctx, slide, cx, y, cardW, 170, item.title, item.lines, { accent: item.accent, fontSize: 15 });
    if (index < items.length - 1) {
      ctx.addShape(slide, {
        x: cx + cardW + 8,
        y: y + 78,
        width: gap - 16,
        height: 4,
        fill: colors.orange,
        line: { style: "solid", fill: colors.orange, width: 0 },
      });
      ctx.addShape(slide, {
        geometry: "triangle",
        x: cx + cardW + gap - 16,
        y: y + 70,
        width: 18,
        height: 20,
        fill: colors.orange,
        line: { style: "solid", fill: colors.orange, width: 0 },
      });
    }
  });
}

function addCompactFlow(ctx, slide, x, y, items) {
  const cardW = 190;
  const cardH = 132;
  const gap = 32;
  items.forEach((item, index) => {
    const cx = x + index * (cardW + gap);
    addCard(ctx, slide, cx, y, cardW, cardH, item.title, item.lines, { accent: item.accent, fontSize: 14 });
    if (index < items.length - 1) {
      ctx.addShape(slide, {
        x: cx + cardW + 8,
        y: y + 62,
        width: gap - 14,
        height: 4,
        fill: colors.orange,
        line: { style: "solid", fill: colors.orange, width: 0 },
      });
      ctx.addShape(slide, {
        geometry: "triangle",
        x: cx + cardW + gap - 14,
        y: y + 54,
        width: 16,
        height: 20,
        fill: colors.orange,
        line: { style: "solid", fill: colors.orange, width: 0 },
      });
    }
  });
}

async function renderPreviews(presentation) {
  await fs.rm(PREVIEW_DIR, { recursive: true, force: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  for (let index = 0; index < presentation.slides.count; index += 1) {
    const slide = presentation.slides.getItem(index);
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(path.join(PREVIEW_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`), Buffer.from(await png.arrayBuffer()));
  }
}

async function main() {
  process.env.HOME = "C:/Users/egork";
  await ensureArtifactToolWorkspace(WORKSPACE);
  const artifact = await importArtifactTool(WORKSPACE);
  const { FileBlob, PresentationFile } = artifact;
  const ctx = createSlideContext(artifact, {
    workspaceDir: WORKSPACE,
    titleFont: "Aptos Display",
    bodyFont: "Aptos",
  });

  const presentation = await PresentationFile.importPptx(await FileBlob.load(SOURCE_PPTX));

  const blankSource = presentation.slides.getItem(6);
  const digitalSlide = await blankSource.duplicate();
  digitalSlide.setIndex(8);
  const telemetrySlide = await blankSource.duplicate();
  telemetrySlide.setIndex(9);

  const slides = Array.from({ length: presentation.slides.count }, (_, index) => presentation.slides.getItem(index));

  setText(textElements(slides[0]).find((element) => textOf(element).includes("Разработка системы")) || titleElement(slides[0]),
    "Разработка программно-аппаратного комплекса предиктивного обслуживания узлов робота-паллетизатора",
    { fontSize: 38, color: colors.white, typeface: "Aptos Display" });
  const author = textElements(slides[0]).find((element) => textOf(element).includes("Миронов"));
  if (author) {
    setText(author, "Миронов Е.М. группа РК9-83Б\nНаучный руководитель – Сащенко Д.В.\n\n2026", {
      fontSize: 20,
      color: colors.white,
      typeface: "Aptos",
    });
  }

  setTitle(slides[1], "Актуальность");
  addCard(ctx, slides[1], 92, 286, 250, 155, "Простои", ["останов робота блокирует", "выход готовой продукции"], { accent: colors.orange });
  addCard(ctx, slides[1], 382, 286, 250, 155, "Регламент", ["не учитывает фактическое", "состояние приводов", "и механических узлов"], { accent: colors.blue });
  addCard(ctx, slides[1], 672, 286, 250, 155, "Телеметрия", ["момент, скорость, фаза", "цикла доступны из модели"], { accent: colors.green });
  addCard(ctx, slides[1], 962, 286, 250, 155, "PdM", ["прогноз RUL позволяет", "планировать обслуживание"], { accent: colors.orange });
  addBullets(ctx, slides[1], 130, 504, 1040, 96, [
    "ВКР переводит задачу от статической оценки надежности к проверяемому ПАК с данными, признаками, прогнозом и мониторингом.",
  ], { fontSize: 22, color: colors.white });

  setTitle(slides[2], "Цель и задачи");
  addCard(ctx, slides[2], 92, 274, 462, 250, "Цель работы", [
    "Разработать и апробировать прототип ПАК",
    "предиктивного обслуживания узлов робота-паллетизатора",
    "на базе цифровой модели, телеметрии и прогноза RUL.",
  ], { accent: colors.orange, fontSize: 18 });
  addCard(ctx, slides[2], 612, 274, 560, 250, "Ключевые задачи", [
    "1. Описать объект и требования к системе.",
    "2. Построить цифровую модель цикла паллетизации.",
    "3. Организовать сбор и обработку телеметрии.",
    "4. Рассчитать признаки деградации и RUL.",
    "5. Проверить качество прогноза и эффект внедрения.",
  ], { accent: colors.blue, fontSize: 18 });

  setTitle(slides[3], "Производственная линия");
  addCard(ctx, slides[3], 220, 600, 842, 86, "Контекст внедрения", [
    "Роботизированная паллетизация находится на выходе линии розлива: отказ узла влияет на накопление готовой продукции и простой участка.",
  ], { accent: colors.orange, fontSize: 17 });

  setTitle(slides[4], "Участок паллетизации");
  addCard(ctx, slides[4], 808, 520, 360, 148, "Рабочий цикл", [
    "4 картонных листа",
    "12 упаковок воды за цикл",
    "перемещение загруженного паллета",
    "повторяемые фазы - основа диагностики",
  ], { accent: colors.blue, fontSize: 16 });

  setTitle(slides[5], "Объект исследования");
  addCard(ctx, slides[5], 70, 430, 338, 204, "ABB IRB 660-180/3.15", [
    "грузоподъемность 180 кг",
    "рабочий радиус до 3,15 м",
    "контролируемые приводы: motor1...motor4",
    "переносимая упаковка: 63 кг",
  ], { accent: colors.orange, fontSize: 16 });

  setTitle(slides[6], "Концепция PdM");
  addFlow(ctx, slides[6], 92, 316, [
    { title: "Сбор данных", lines: ["момент", "скорость", "фаза цикла"], accent: colors.blue },
    { title: "Признаки", lines: ["RMS", "энергия", "длительность"], accent: colors.green },
    { title: "Прогноз", lines: ["HI", "RUL", "порог состояния"], accent: colors.orange },
    { title: "Решение", lines: ["алерт", "рекомендация", "план ТО"], accent: colors.blue },
  ]);
  addBullets(ctx, slides[6], 135, 545, 980, 70, [
    "Система обслуживает не календарный интервал, а фактическую динамику состояния узла.",
  ], { fontSize: 22, color: colors.white });

  setTitle(slides[7], "Цифровая модель в CoppeliaSim");
  addCard(ctx, slides[7], 74, 286, 346, 132, "Состав сцены", [
    "робот /base_respondable",
    "конвейеры бутылок и паллет",
    "шаблоны упаковок и картона",
  ], { accent: colors.blue, fontSize: 16 });
  addCard(ctx, slides[7], 74, 442, 346, 132, "Цикл паллетизации", [
    "захват листов и упаковок",
    "укладка слоями",
    "событие cycle_complete",
  ], { accent: colors.orange, fontSize: 16 });
  await ctx.addImage(slides[7], {
    path: ASSETS.cellScheme,
    x: 472,
    y: 248,
    width: 690,
    height: 388,
    fit: "contain",
    alt: "Схема роботизированной ячейки",
  });

  setTitle(slides[8], "Телеметрия и диагностические признаки");
  addCard(ctx, slides[8], 80, 278, 332, 150, "Собираемые поля", [
    "time, cycle, phase, axis",
    "q, omega, accel, torque",
    "layer, item, carrying",
  ], { accent: colors.blue, fontSize: 16 });
  addCard(ctx, slides[8], 80, 452, 332, 150, "Признаки", [
    "mean / max / std / rms",
    "energy и slope",
    "длительность фазы",
  ], { accent: colors.green, fontSize: 16 });
  await ctx.addImage(slides[8], {
    path: ASSETS.torque,
    x: 472,
    y: 262,
    width: 702,
    height: 386,
    fit: "contain",
    alt: "RMS момента по осям",
  });

  deleteTextExceptTitle(slides[9]);
  deleteImages(slides[9]);
  setTitle(slides[9], "Архитектура разработанного ПАК");
  addFlow(ctx, slides[9], 72, 286, [
    { title: "Цифровая модель", lines: ["CoppeliaSim", "motor1...motor4", "фазы цикла"], accent: colors.blue },
    { title: "Сбор данных", lines: ["Python", "Remote API", "JSONL/CSV"], accent: colors.green },
    { title: "Признаки", lines: ["валидация", "RMS / energy", "длительность фаз"], accent: colors.orange },
    { title: "Аналитика", lines: ["HI(motor1...motor4)", "RUL(motor1...motor4)", "MLPRegressor"], accent: colors.blue },
  ]);
  addCard(ctx, slides[9], 240, 510, 300, 126, "Хранилище", [
    "InfluxDB",
    "события цикла",
    "прогнозы и метрики",
  ], { accent: colors.green, fontSize: 16 });
  addCard(ctx, slides[9], 740, 510, 300, 126, "Интерфейс", [
    "Grafana",
    "панели HI/RUL",
    "предупреждения по ТО",
  ], { accent: colors.orange, fontSize: 16 });
  ctx.addShape(slides[9], { x: 542, y: 570, width: 190, height: 4, fill: colors.orange, line: { style: "solid", fill: colors.orange, width: 0 } });
  ctx.addShape(slides[9], { geometry: "triangle", x: 718, y: 562, width: 18, height: 20, fill: colors.orange, line: { style: "solid", fill: colors.orange, width: 0 } });

  deleteTextExceptTitle(slides[10]);
  deleteImages(slides[10]);
  replaceWithTopTitle(ctx, slides[10], "Алгоритм оценки RUL");
  addCompactFlow(ctx, slides[10], 98, 300, [
    { title: "1. Сбор", lines: ["момент", "скорость", "фаза цикла"], accent: colors.blue },
    { title: "2. Валидация", lines: ["фильтрация", "проверка полноты", "сегментация"], accent: colors.green },
    { title: "3. Признаки", lines: ["RMS", "energy", "duration"], accent: colors.orange },
    { title: "4. HI / RUL", lines: ["контролируемые", "приводы", "motor1...motor4"], accent: colors.blue },
    { title: "5. ТО", lines: ["порог RUL", "предупреждение", "рекомендация"], accent: colors.green },
  ]);
  addBullets(ctx, slides[10], 160, 510, 900, 72, [
    "Алгоритм превращает фазовую телеметрию в оценку остаточного ресурса и предупреждение для обслуживания.",
  ], { fontSize: 22, color: colors.white });

  deleteTextExceptTitle(slides[11]);
  deleteImages(slides[11]);
  replaceWithTopTitle(ctx, slides[11], "Модель деградации узлов");
  addCard(ctx, slides[11], 86, 250, 340, 140, "Сценарии S0-S3", [
    "S0: нормальный режим",
    "S1-S2: слабая и средняя деградация",
    "S3: ускоренное ухудшение состояния",
  ], { accent: colors.orange, fontSize: 16 });
  addCard(ctx, slides[11], 86, 420, 340, 140, "Health Indicator", [
    "HI снижается с накоплением повреждения",
    "предельное состояние задает RUL",
  ], { accent: colors.green, fontSize: 16 });
  await ctx.addImage(slides[11], {
    path: ASSETS.hi,
    x: 482,
    y: 220,
    width: 682,
    height: 410,
    fit: "contain",
    alt: "Кривые HI",
  });

  deleteTextExceptTitle(slides[12]);
  deleteImages(slides[12]);
  replaceWithTopTitle(ctx, slides[12], "Результаты апробации ПАК");
  addMetric(ctx, slides[12], 92, 260, 250, 122, "22174", "сырых пакета телеметрии", { accent: colors.blue });
  addMetric(ctx, slides[12], 376, 260, 250, 122, "88696", "нормализованных строк", { accent: colors.blue });
  addMetric(ctx, slides[12], 660, 260, 250, 122, "600", "строк фазовых признаков", { accent: colors.green });
  addMetric(ctx, slides[12], 944, 260, 250, 122, "192000", "RUL-оценок и нейросетевых прогнозов", { accent: colors.green, valueSize: 25 });
  addMetric(ctx, slides[12], 234, 432, 250, 122, "K_data = 1.000", "валидность данных", { accent: colors.orange, valueSize: 22 });
  addMetric(ctx, slides[12], 516, 432, 250, 122, "K_phase = 1.000", "покрытие фаз цикла", { accent: colors.orange, valueSize: 22 });
  addMetric(ctx, slides[12], 798, 432, 250, 122, "14 фаз", "выделено в полном цикле", { accent: colors.orange, valueSize: 24 });

  deleteTextExceptTitle(slides[13]);
  deleteImages(slides[13]);
  replaceWithTopTitle(ctx, slides[13], "Качество прогноза RUL", { color: "#000000", y: 78, fontSize: 38 });
  await ctx.addImage(slides[13], {
    path: ASSETS.rul,
    x: 80,
    y: 176,
    width: 810,
    height: 456,
    fit: "contain",
    alt: "Фактический и прогнозный RUL",
  });
  addMetric(ctx, slides[13], 934, 226, 236, 88, "MAE = 1.441", "средняя абсолютная ошибка, циклы", { accent: colors.blue, valueSize: 23 });
  addMetric(ctx, slides[13], 934, 334, 236, 88, "RMSE = 2.144", "среднеквадратичная ошибка, циклы", { accent: colors.orange, valueSize: 23 });
  addMetric(ctx, slides[13], 934, 442, 236, 88, "R² = 0.988", "качество аппроксимации", { accent: colors.green, valueSize: 26 });
  addMetric(ctx, slides[13], 934, 538, 236, 104, "MLPRegressor", "сценарии S0-S3, модельные деградационные данные", { accent: colors.blue, valueSize: 21, labelSize: 14 });
  addBodyText(ctx, slides[13], "Метрики получены на модельных деградационных сценариях S0-S3.", 160, 650, 760, 34, {
    fontSize: 16,
    color: colors.muted,
  });

  deleteTextExceptTitle(slides[14]);
  deleteImages(slides[14]);
  replaceWithTopTitle(ctx, slides[14], "Операторский мониторинг");
  addCard(ctx, slides[14], 72, 270, 310, 144, "Назначение", [
    "показывать состояние узлов",
    "фиксировать события цикла",
    "выдавать предупреждения по RUL",
  ], { accent: colors.blue, fontSize: 16 });
  addCard(ctx, slides[14], 72, 446, 310, 144, "Инфраструктура", [
    "InfluxDB: хранение рядов",
    "Grafana: панели и алерты",
    "средний шаг записи: 0.093 с",
    "обновление панели: 5 с",
  ], { accent: colors.orange, fontSize: 16 });
  await ctx.addImage(slides[14], {
    path: ASSETS.dashboard,
    x: 438,
    y: 246,
    width: 744,
    height: 410,
    fit: "contain",
    alt: "Сводка дашборда ПАК",
  });

  deleteTextExceptTitle(slides[15]);
  replaceWithTopTitle(ctx, slides[15], "Экономический эффект и выводы");
  addMetric(ctx, slides[15], 104, 270, 300, 126, "450000 руб/год", "расчетный эффект от снижения потерь и простоев", { accent: colors.orange, valueSize: 25 });
  addMetric(ctx, slides[15], 490, 270, 300, 126, "1.0 год", "ориентировочный срок окупаемости", { accent: colors.green, valueSize: 30 });
  addMetric(ctx, slides[15], 876, 270, 300, 126, "K_pred = 1.000", "прогноз доступен для проверенных данных", { accent: colors.blue, valueSize: 25 });
  addCard(ctx, slides[15], 260, 420, 760, 92, "Расчет эффекта", [
    "3 × (8 − 2) × 30000 − 90000 = 450000 руб./год",
  ], { accent: colors.orange, fontSize: 18 });
  addBullets(ctx, slides[15], 146, 530, 996, 120, [
    "Разработан ПАК от цифровой модели до мониторинга оператора.",
    "Получены проверяемые данные, признаки деградации и прогноз RUL.",
    "Результаты подтверждают работоспособность прототипа PdM-контура на модельных данных.",
    "Для промышленного внедрения требуется калибровка на реальной телеметрии и истории отказов.",
  ], { fontSize: 19, color: colors.white });

  setTitle(slides[16], "Спасибо за внимание!");
  addBodyText(ctx, slides[16], "Разработка программно-аппаратного комплекса предиктивного обслуживания узлов робота-паллетизатора", 165, 382, 930, 70, {
    fontSize: 26,
    color: colors.white,
    bold: false,
  });
  addBodyText(ctx, slides[16], "Миронов Е.М. | РК9-83Б | 2026", 410, 478, 500, 42, {
    fontSize: 22,
    color: colors.white,
    bold: false,
  });

  if (presentation.slides.count !== 17) {
    throw new Error(`Expected 17 slides, got ${presentation.slides.count}`);
  }

  await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  await renderPreviews(presentation);
  console.log(JSON.stringify({ finalPptx: FINAL_PPTX, slideCount: presentation.slides.count, previewDir: PREVIEW_DIR }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
