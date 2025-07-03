# No Money for Cultivation - Translation Project

### Prompts

You are a master light novel translator and an expert English teacher. Your task is to translate the following Chinese light novel text into English, with the specific goal of creating a version that is suitable for a B1-level English learner.

The story is a dark-fantasy cultivation story set in a dystopian, hyper-capitalist world where even the path to immortality is commercialized. The protagonist, Zhang Yu, is a poor student trying to survive in this system.

Your translation must adhere to the following principles:

1.  **Preserve Original Intent:** Maintain the original dark, satirical, and desperate tone. The translation should feel natural and engaging, not like a literal, word-for-word machine translation that results in "Chinglish."
2.  **Rewrite for B1-Level Clarity:** Adapt sentence structures to be clear and idiomatic in English. Use vocabulary and grammar appropriate for a B1 proficiency level. Avoid overly complex or obscure words, but don't oversimplify to the point of losing the original flavor. Rewrite sentences to sound as if they were originally written by a native English speaker.
3.  **Line-by-Line Formatting with Context:** Your translation must follow the original line-by-line structure. For each line, append a contextual marker with the format `[[{index} role emotion]]`.
    *   `{index}`: The original line number from the source text.
    *   `role`: The speaker or context. Use the character's Chinese name (e.g., `张羽`, `白真真`), `旁白` for narration, or `陌生男1`/`陌生女1` for new/unnamed characters. Refer to the `translation_reference.md` for established character names.
    *   `emotion`: The dominant emotion of the line. Choose one from: `neutral`, `happy`, `angry`, `sad`
    *   **Example**:
        *   **Source:** `"你每天竟然要睡五个小时，那就是每天要比别人少学三个小时，九年就差了近一万个小时……" [[20]]`
        *   **Output:** `"You actually sleep five hours a day? That means you study three hours less than others every day. Over nine years, that's almost ten thousand hours..." [[20 面试官 angry]]`
        *   **Source:** `他只知道昆墟之内，是一个以仙道各大宗门为尊的世界。 [[145]]`
        *   **Output:** `He only knew that within Kunxu, it was a world where the major cultivation sects were supreme. [[145 旁白 neutral]]`
4.  **Consistency:** Use the provided `books/nomoney_en/cn/translation_reference.md` file to ensure consistent translation of character names, specific terms, and locations.
5. Save the final, formatted result directly into a new .txt file (e.g., 0001.txt) within the `/books/nomoney_en/` folder.
Translate the text from `books/nomoney_en/cn/cn_new.txt` following these instructions. 