# Photographing pages for OCR

In testing, how a page was photographed changed the error rate more than any
setting: the same OCR scored 12% on one textbook photo and 80% on another.
These guidelines come from what failed in the test photos.

## Taking the photo

1. **Lay the page flat.** Press a book open, or use a pecha leaf on a table.
   Curved pages bend lines and the OCR skips them.
2. **Use even light with no shadows.** Daylight from a window, or two lamps
   from either side. Shadows from your hand or phone were behind the worst
   results (`textbook_image5`: 75% error before shadow handling).
3. **Fill the frame with the page.** Keep tables, hands, and other pages out
   of the picture. A dark table in the frame broke `textbook_image4`.
4. **Hold the phone straight above the page,** parallel to it, not at an angle.
5. **Get close enough to read the small marks.** Vowel signs, the tsheg (་),
   and stacked letters should be sharp when you zoom in. Tap to focus.
6. **No highlighter or pen marks** if you can avoid them. A highlighted
   heading was missed in `textbook_image`.
7. **Avoid show-through.** If text from the back of a thin page shows, put a
   sheet of plain dark paper behind it.

## For the test set

- **One section per image.** Crop to a few lines or one paragraph; short crops
  are quicker to transcribe and easier to check.
- **Name the transcript after the image:** `test_data/pecha_01.jpg` →
  `ground_truth/pecha_01.txt`. Check the filename has no stray characters if
  you type it with the Dzongkha keyboard on.
- **Type exactly what is on the page,** one line of text per line, including
  tsheg and shad. Don't correct spelling.
- **Chöke texts** (prayers, pechas): tell Claude the filenames, or add them to
  `CATEGORIES` in `src/evaluate.py` as `"choekey"`, so their score is reported
  next to Dzongkha rather than mixed in.
- **Aim for variety:** printed prayer books, pecha pages (woodblock and
  modern print), different fonts and sizes, a few deliberately hard photos.
- **Privacy:** don't include names or personal details, since test images go
  into the public repo.
