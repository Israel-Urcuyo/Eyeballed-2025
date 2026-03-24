//
//  main.swift
//  eyeballed
//
//  Created by marvin industan on 6/24/25.
//

import Foundation
import Vision
import AppKit

func runOCR() {
    let inputImagePath = "shared/input.jpg"
    let outputTextPath = "shared/output.txt"

    guard let image = NSImage(contentsOfFile: inputImagePath),
          let tiffData = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let ciImage = CIImage(bitmapImageRep: bitmap) else {
        try? "[ERROR] Image load failed.".write(toFile: outputTextPath, atomically: true, encoding: .utf8)
        exit(1)
    }

    var extractedText = ""
    let semaphore = DispatchSemaphore(value: 0)

    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            extractedText = "[ERROR] OCR failed: \(error.localizedDescription)"
        } else if let observations = request.results as? [VNRecognizedTextObservation] {
            let lines = observations.compactMap { $0.topCandidates(1).first?.string }
            extractedText = lines.joined(separator: "\n")
        } else {
            extractedText = "[ERROR] No text found."
        }
        semaphore.signal()
    }

    request.recognitionLanguages = ["en-US"]
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        extractedText = "[ERROR] OCR execution failed: \(error.localizedDescription)"
        semaphore.signal()
    }

    semaphore.wait()

    do {
        try FileManager.default.createDirectory(atPath: "shared", withIntermediateDirectories: true)
        try extractedText.write(toFile: outputTextPath, atomically: true, encoding: .utf8)
    } catch {
        try? "[ERROR] Failed to write output: \(error.localizedDescription)".write(toFile: outputTextPath, atomically: true, encoding: .utf8)
        exit(1)
    }
}

runOCR()
