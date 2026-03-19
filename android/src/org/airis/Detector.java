package org.airis;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import org.json.JSONArray;
import org.json.JSONObject;
import org.tensorflow.lite.Interpreter;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Detector {

    private static final int INPUT_SIZE = 320;
    private static final int NUM_DETECTIONS = 10;
    private static Interpreter interpreter;
    private static List<String> labels = new ArrayList<>();

    public static synchronized boolean initialize(Activity activity, String modelPath, String labelsPath) {
        if (interpreter != null) {
            return true;
        }

        try {
            File modelFile = new File(modelPath);
            if (!modelFile.exists()) {
                return false;
            }

            MappedByteBuffer modelBuffer;
            try (FileInputStream input = new FileInputStream(modelFile);
                 FileChannel channel = input.getChannel()) {
                modelBuffer = channel.map(FileChannel.MapMode.READ_ONLY, 0, channel.size());
            }

            Interpreter.Options options = new Interpreter.Options();
            options.setNumThreads(4);
            interpreter = new Interpreter(modelBuffer, options);

            labels = new ArrayList<>();
            try (BufferedReader reader = new BufferedReader(new FileReader(labelsPath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    labels.add(line.trim());
                }
            }

            return true;
        } catch (Exception e) {
            interpreter = null;
            return false;
        }
    }

    public static synchronized String analyze(String imagePath) {
        try {
            if (interpreter == null) {
                return "[]";
            }

            Bitmap bitmap = BitmapFactory.decodeFile(imagePath);
            if (bitmap == null) {
                return "[]";
            }

            Bitmap resized = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true);
            ByteBuffer input = convertBitmap(resized);

            float[][][] locations = new float[1][NUM_DETECTIONS][4];
            float[][] classes = new float[1][NUM_DETECTIONS];
            float[][] scores = new float[1][NUM_DETECTIONS];
            float[] numDetections = new float[1];

            Object[] inputArray = {input};
            Map<Integer, Object> outputMap = new HashMap<>();
            outputMap.put(0, locations);
            outputMap.put(1, classes);
            outputMap.put(2, scores);
            outputMap.put(3, numDetections);
            interpreter.runForMultipleInputsOutputs(inputArray, outputMap);

            int count = Math.min(NUM_DETECTIONS, (int) numDetections[0]);
            JSONArray result = new JSONArray();
            for (int i = 0; i < count; i++) {
                float score = scores[0][i];
                if (score < 0.20f) {
                    continue;
                }

                int labelIndex = (int) classes[0][i];
                String label = labelIndex >= 0 && labelIndex < labels.size()
                    ? labels.get(labelIndex)
                    : "object";

                JSONObject item = new JSONObject();
                item.put("label", label);
                item.put("score", score);
                item.put("ymin", locations[0][i][0]);
                item.put("xmin", locations[0][i][1]);
                item.put("ymax", locations[0][i][2]);
                item.put("xmax", locations[0][i][3]);
                result.put(item);
            }

            return result.toString();
        } catch (Exception e) {
            return "[]";
        }
    }

    private static ByteBuffer convertBitmap(Bitmap bitmap) {
        ByteBuffer buffer = ByteBuffer.allocateDirect(1 * INPUT_SIZE * INPUT_SIZE * 3 * 4);
        buffer.order(ByteOrder.nativeOrder());

        int[] pixels = new int[INPUT_SIZE * INPUT_SIZE];
        bitmap.getPixels(pixels, 0, INPUT_SIZE, 0, 0, INPUT_SIZE, INPUT_SIZE);

        int pixelIndex = 0;
        for (int y = 0; y < INPUT_SIZE; y++) {
            for (int x = 0; x < INPUT_SIZE; x++) {
                int pixel = pixels[pixelIndex++];
                float r = ((pixel >> 16) & 0xFF) / 255.0f;
                float g = ((pixel >> 8) & 0xFF) / 255.0f;
                float b = (pixel & 0xFF) / 255.0f;
                buffer.putFloat(r);
                buffer.putFloat(g);
                buffer.putFloat(b);
            }
        }

        buffer.rewind();
        return buffer;
    }
}
