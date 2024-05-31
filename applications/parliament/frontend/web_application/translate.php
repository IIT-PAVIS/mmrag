<?php
require 'vendor/autoload.php';

use Stichoza\GoogleTranslate\GoogleTranslate;

function translateText($text, $targetLanguage) {
    try {
        // Crea una nuova istanza di GoogleTranslate
        $tr = new GoogleTranslate();

        // Imposta la lingua di destinazione
        $tr->setTarget($targetLanguage);

        // Traduci il testo
        $translatedText = $tr->translate($text);

        // Restituisci il testo tradotto
        return $translatedText;
    } catch (Exception $e) {
        return 'Error: ' . $e->getMessage();
    }
}
