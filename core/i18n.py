TEXTS = {
    "en": {
        "start-welcome": "👋 **Welcome!** Let's set up your profile.\n\nEnter your **ICR** (carbs per 1U insulin):",
        "enter-isf": "✅ Got it. Now enter your **ISF** (BG drop per 1U insulin):",
        "enter-target": "🎯 What is your **target** blood glucose? (mmol/L):",
        "enter-insulin": "💉 Which **insulin** do you use? (e.g., NovoRapid):",
        "reg-complete": "🎉 **Registration complete!**\n\nYou can now send me food photos for analysis.",
        "already-reg": "👋 **You are already registered!**\n\nSend a photo to analyze your meal or use the menu below.",
        "error-number": "⚠️ **Please enter a valid number.**",
        "analyzing": "🔍 **Analyzing your meal...** Please wait.",
        "not-found": "❌ **Sorry, couldn't find nutrition data for this dish.**",
        "ask-bg": "🥗 **{dish}** (~{weight}g)\n📊 Carbs: **{carbs}g**\n\n{line}\n🩸 Enter your **current glucose** (mmol/L) or send /skip:",
        "result-bolus": "💉 **Suggested bolus: {total} U** ({type})\n\n• Carb dose: `{carb_dose} U`\n• Correction: `{correction} U`\n\n📊 **Macros for {dish}:**\nCarbs: **{carbs}g** | Kcal: **{kcal}**\n\n⚠️ _Verify with your doctor!_",
        "history-header": "📜 **Your last 10 meals:**\n",
        "history-item": "🗓 {date} | **{dish}**\n   Carbs: `{carbs}g` | Dose: `{bolus}U`",
        "history-empty": "📭 **Your history is empty.**",
        "settings-main": "⚙️ **Your Settings:**\n\n🌍 Language: **{lang}**\n🔢 ICR: `{icr}`\n📉 ISF: `{isf}`\n🎯 Target BG: `{target}`\n💉 Insulin: `{type}`\n\n**Choose an action:**",
        "btn-change-lang": "🌍 Change Language",
        "lang-changed": "✅ Language changed to **English**!",
        "select-lang": "🌍 **Select your language:**",
        "menu-main": "🏠 **Main Menu**\nSend me a photo of your meal.",
        "btn-history": "📜 History",
        "btn-settings": "⚙️ Settings",
        "btn-new-photo": "📸 New Photo",
        "prompt-photo": "📸 **Ready!**\n\nTap the attachment icon (📎) below to send or take a photo of your meal.",
    },
    "uk": {
        "start-welcome": "👋 **Вітаю!** Давайте налаштуємо ваш профіль.\n\nВведіть ваш **ICR** (кількість вуглеводів на 1 од. інсуліну):",
        "enter-isf": "✅ Зрозумів. Тепер введіть ваш **ISF** (на скільки ммоль/л знижує цукор 1 од. інсуліну):",
        "enter-target": "🎯 Який ваш **цільовий** рівень цукру? (ммоль/л):",
        "enter-insulin": "💉 Який **інсулін** ви використовуєте? (наприклад, НовоРапід):",
        "reg-complete": "🎉 **Реєстрацію завершено!**\n\nТепер ви можете надсилати мені фото їжі для аналізу.",
        "already-reg": "👋 **Ви вже зареєстровані!**\n\nНадішліть фото для аналізу або скористайтеся меню нижче.",
        "error-number": "⚠️ **Будь ласка, введіть коректне число.**",
        "analyzing": "🔍 **Аналізую вашу страву...** Зачекайте.",
        "not-found": "❌ **Вибачте, не вдалося знайти дані про поживну цінність цієї страви.**",
        "ask-bg": "🥗 **{dish}** (~{weight}г)\n📊 Вуглеводи: **{carbs}г**\n\n{line}\n🩸 Введіть ваш **поточний цукор** (ммоль/л) або надішліть /skip:",
        "result-bolus": "💉 **Рекомендована доза: {total} од.** ({type})\n\n• На вуглеводи: `{carb_dose} од.`\n• Корекція: `{correction} од.`\n\n📊 **Макроси для {dish}:**\nВуглеводи: **{carbs}г** | Ккал: **{kcal}**\n\n⚠️ _Перевірте з вашим лікарем!_",
        "history-header": "📜 **Ваші останні 10 прийомів їжі:**\n",
        "history-item": "🗓 {date} | **{dish}**\n   Вуглеводи: `{carbs}г` | Доза: `{bolus}од.`",
        "history-empty": "📭 **Ваша історія порожня.**",
        "settings-main": "⚙️ **Ваші налаштування:**\n\n🌍 Мова: **{lang}**\n🔢 ICR: `{icr}`\n📉 ISF: `{isf}`\n🎯 Цільовий цукор: `{target}`\n💉 Інсулін: `{type}`\n\n**Оберіть дію:**",
        "btn-change-lang": "🌍 Змінити мову",
        "lang-changed": "✅ Мову змінено на **українську**!",
        "select-lang": "🌍 **Оберіть мову:**",
        "menu-main": "🏠 **Головне меню**\nНадішліть мені фото їжі.",
        "btn-history": "📜 Історія",
        "btn-settings": "⚙️ Налаштування",
        "btn-new-photo": "📸 Нове фото",
        "prompt-photo": "📸 **Готово!**\n\nНатисніть на значок скріпки (📎) внизу, щоб надіслати або зробити фото вашої страви.",
    },
}


class I18n:
    def __init__(self, lang: str):
        self.lang = lang

    def get(self, key: str, **kwargs) -> str:
        text = TEXTS.get(self.lang, TEXTS["en"]).get(key, key)
        # Helper for a horizontal line
        if "{line}" in text:
            text = text.replace("{line}", "—" * 20)
        return text.format(**kwargs)
