import numpy as np
import os
from scipy.io import wavfile
from scipy.signal import butter, lfilter, stft, istft
import random


def apply_volume_changes(data, sample_rate, temperature=1):
    edited_data = np.empty(0, dtype=np.float32)
    total_samples = data.shape[0]

    # Current sample index
    current_sample = 0

    amp_1=1
    amp_2=1

    while current_sample < total_samples:
        segment_length_samples = int(random.uniform(0.1, temperature) * sample_rate)
        end_sample = min(current_sample + segment_length_samples, total_samples)

        segment = data[current_sample:end_sample]

        if random.random() < temperature/10:
            edited_data = np.append(edited_data, segment)
            current_sample = end_sample
            return edited_data

        volume_change = random.uniform(0.5/(temperature*amp_2), temperature*amp_2)
        segment = segment * volume_change

        edited_data = np.append(edited_data, segment)

        current_sample = end_sample

    return edited_data

#temperature max = 10
def apply_fmask(data, sample_rate, temperature=1, fmask_function = lambda f: np.ones(len(f))):
    edited_data = np.empty(0, dtype=np.float32)
    total_samples = data.shape[0]
    current_sample = 0

    while current_sample < total_samples:
        # Random segment length between 0.1 and 1 seconds
        segment_length_samples = int(random.uniform(0.1, 1) * sample_rate)
        end_sample = min(current_sample + segment_length_samples, total_samples)
        segment = data[current_sample:end_sample]

        # doesn't change random fragments of audio
        if random.random() < temperature/10:
            edited_data = np.append(edited_data, segment)
            current_sample = end_sample
            continue

        f, t, Zxx = stft(segment, fs=sample_rate, nperseg=1024)
        mask = fmask_function(f)
        Zxx_masked = Zxx * mask[:, np.newaxis]

        _, x_reconstructed = istft(Zxx_masked, fs=sample_rate)
        x_reconstructed = normalize_audio(x_reconstructed)

        edited_data = np.append(edited_data, x_reconstructed)
        current_sample = end_sample

    return edited_data

def normalize_audio_rms(audio):
    """
    Normalize the audio based on RMS value to aim for a consistent perceived loudness
    """
    rms = np.sqrt(np.mean(np.square(audio)))
    desired_rms = 0.1  # Arbitrary target RMS value for normalization
    audio = audio * (desired_rms / rms)
    audio = np.clip(audio, -1, 1)  # Ensure audio remains in the -1 to 1 range
    return audio

def normalize_audio(audio):
    """
    Normalize the audio to -1 to 1 range
    """
    audio_max = np.max(np.abs(audio))
    if audio_max > 0:
        audio = audio / audio_max
    return audio
    return audio

def apply_three(data, sample_rate, temperature=1):
    edited_data = np.empty(0, dtype=np.float32)
    total_samples = data.shape[0]
    current_sample = 0

    while current_sample < total_samples:
        # Random segment length between 0.1 and 1 seconds
        segment_length_samples = int(random.uniform(0.2, 0.7) * sample_rate)
        end_sample = min(current_sample + segment_length_samples, total_samples)
        segment = data[current_sample:end_sample]

        m = random.choice(["gauss", "sin", "whisper", "shout"])

        f, t, Zxx = stft(segment, fs=sample_rate, nperseg=1024)

        # doesn't change random fragments of audio
        if random.random() > temperature/10:
            #print("done")
            x_reconstructed = normalize_audio(segment)

        elif m=="gauss":
            #print("gauss")
            mask = None
            gaussian_mask = np.exp(-0.5 * ((f - 1000) / 200) ** 2)
            Zxx_masked = Zxx * gaussian_mask[:, np.newaxis]
            _, x_reconstructed = istft(Zxx_masked, fs=sample_rate)
            x_reconstructed = normalize_audio(x_reconstructed)

        elif m=="sin":
            #print("sin")
            sin_mask = np.sin(f*0.3)
            Zxx_masked = Zxx * sin_mask[:, np.newaxis]
            _, x_reconstructed = istft(Zxx_masked, fs=sample_rate)
            x_reconstructed = normalize_audio(x_reconstructed)

        elif m=="whisper":
            #print("whisper")
            whisper_mask = np.interp(f, [0, np.max(f)*0.056, np.max(f)*0.4, np.max(f)], [0, 0, 1, 1])
            Zxx_masked = Zxx * whisper_mask[:, np.newaxis]*np.sin(f)[:, np.newaxis]
            _, x_reconstructed = istft(Zxx_masked, fs=sample_rate)
            noise=np.random.normal(0, 1, x_reconstructed.shape[0])/50
            x_reconstructed = normalize_audio(x_reconstructed) + noise
            x_reconstructed = x_reconstructed*2

        elif m == "shout":
            #print("shout")
            # Step 1: Apply shout mask to amplify the frequency spectrum
            shout_mask = np.interp(f, [0, np.max(f)], [1.2, 1.2])
            Zxx_masked = Zxx * shout_mask[:, np.newaxis]

            # Step 2: Convert back to time domain
            _, x_reconstructed = istft(Zxx_masked, fs=sample_rate)
            x_reconstructed = normalize_audio(x_reconstructed)

            # Step 3: Apply soft clipping to the time-domain signal for distortion
            threshold = 0.4  # Threshold for soft clipping
            # Ensure the signal is in the range -1 to 1
            x_reconstructed = np.clip(x_reconstructed, -1, 1)
            # Apply soft clipping
            x_reconstructed = np.where(np.abs(x_reconstructed) < threshold,
                                    x_reconstructed,
                                    np.sign(x_reconstructed) * (threshold + (1 - threshold) * np.log(1 + np.abs(x_reconstructed - threshold) / (1 - threshold))))


        edited_data = np.append(edited_data, x_reconstructed)
        current_sample = end_sample

    return edited_data


def insert_audio_segment(main_file, insert_file, output_file, replace=False):
    # Read the main audio file
    main_rate, main_data = wavfile.read(main_file)

    # Read the insert audio file
    insert_rate, insert_data = wavfile.read(insert_file)

    # Ensure both audio files have the same sample rate
    if main_rate != insert_rate:
        raise ValueError("Sample rates of the audio files do not match.")

    # Convert to mono if the audio is stereo
    if len(main_data.shape) > 1:
        main_data = main_data.mean(axis=1).astype(main_data.dtype)
    if len(insert_data.shape) > 1:
        insert_data = insert_data.mean(axis=1).astype(insert_data.dtype)

    main_length = main_data.shape[0]
    insert_length = insert_data.shape[0]

    # Randomize length and place of sampling of the insert sound
    max_insert_segment_length = min(insert_length, main_length // 2, 3*insert_rate) # fragment can be no longer than 3 seconds

    random_segment_length = random.randint(1, max_insert_segment_length)
    start_sample = random.randint(0, insert_length - random_segment_length)
    insert_segment = insert_data[start_sample:start_sample + random_segment_length]

    # Choose a random position to insert the audio segment into the main audio
    insert_position = random.randint(0, main_length - 1)

    if replace:
        # Ensure the insert position does not exceed the main audio length
        if insert_position + random_segment_length > main_length:
            insert_position = main_length - random_segment_length

        # Replace a segment of the main audio with the insert audio segment
        modified_data = np.concatenate([
            main_data[:insert_position],
            insert_segment,
            main_data[insert_position + random_segment_length:]
        ])
    else:
        # Insert the audio segment at a random position
        modified_data = np.concatenate([
            main_data[:insert_position],
            insert_segment,
            main_data[insert_position:]
        ])

    # Write the modified audio to a new file
    wavfile.write(output_file, main_rate, modified_data)

def select_random_filename(directory):
    all_files = os.listdir(directory)
    files = [f for f in all_files if os.path.isfile(os.path.join(directory, f))]
    random_file = random.choice(files)

    # Print the randomly selected file name
    return random_file

def edit_sample(filename, temperature, number_of_inserts, number_of_appends):
    sample_rate, data = wavfile.read(f'./samples/{filename}')
    data = data.astype(np.float32)
    masked_data = apply_three(data, sample_rate, temperature = temperature)
    fully_edited_data = masked_data
    int_data = np.int16((fully_edited_data + 1.0) * 32767.5 - 32768)
    wavfile.write(f'./samples/evolved_{filename}', sample_rate, int_data)

    for number in np.arange(0,number_of_inserts,1):
        file_selected = select_random_filename("./samples/dźwięki_dopasowane/")
        insert_audio_segment(f"./samples/evolved_{filename}", f"./samples/dźwięki_dopasowane/{file_selected}", f"./samples/evolved_{filename}", replace=True)
    for number in np.arange(0,number_of_appends,1):
        file_selected = select_random_filename("./samples/dźwięki_dopasowane/")
        insert_audio_segment(f"./samples/evolved_{filename}", f"./samples/dźwięki_dopasowane/{file_selected}", f"./samples/evolved_{filename}", replace=False)

